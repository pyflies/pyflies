import pytest
from os.path import join, dirname, abspath
from textx import metamodel_from_file, TextXSyntaxError

from pyflies.custom_classes import (custom_classes, CustomClass, Symbol,
                                    OrExpression, BaseValue,
                                    AdditiveExpression, List, String, Range)
from pyflies.exceptions import PyFliesException


this_folder = join(dirname(abspath(__file__)))


def test_time_references():
    """Test for pyflies time references"""

    mm = metamodel_from_file(join(this_folder, 'timeref.tx'))

    # Plain
    ref = mm.model_from_str('10')
    assert ref.relative_op is None
    assert not ref.start_relative
    assert ref.time == 10

    # Positive relative from previous end
    ref = mm.model_from_str('+10')
    assert ref.relative_op == '+'
    assert ref.time == 10
    assert not ref.start_relative

    # Negative relative from previous end
    ref = mm.model_from_str('-10')
    assert ref.relative_op == '-'
    assert ref.time == 10

    # Positive relative from previous start
    ref = mm.model_from_str('.+10')
    assert ref.relative_op == '+'
    assert ref.start_relative
    assert ref.time == 10


def test_expressions_arithmetic():
    """
    Test Pyflies arithmetic expressions.
    """

    mm = metamodel_from_file(join(this_folder, 'expression.tx'), classes=custom_classes)

    exp = mm.model_from_str('2 + 3 * 2 * 3 / 5 - 1')
    assert exp.exp.eval() == 4.6

def test_expressions_comparison_boolean():
    """
    Test Pyflies boolean expressions.
    """

    mm = metamodel_from_file(join(this_folder, 'expression.tx'), classes=custom_classes)

    exp = mm.model_from_str('2 > 1 and 6 <= 8')
    assert exp.exp.eval() is True
    exp = mm.model_from_str('2 > 1 and 6 >= 8')
    assert exp.exp.eval() is False
    exp = mm.model_from_str('2 > 1 or 6 >= 8')
    assert exp.exp.eval() is True
    exp = mm.model_from_str('2 > 1 and (6 >= 8 or 5 < 9)')
    assert exp.exp.eval() is True
    # `and` has higher priority than `or`
    # This will be True only if `and` is evaluated before `or`
    exp = mm.model_from_str('2 > 1 or 6 >= 8 and 9 < 9')
    assert exp.exp.eval() is True


def test_compound_types():
    mm = metamodel_from_file(join(this_folder, 'expression.tx'), classes=custom_classes)

    m = mm.model_from_str('[1, 2, ["some string", 4.5], 3]')
    meval = m.exp.eval()
    assert meval == [1, 2, ['some string', 4.5], 3]

    m = mm.model_from_str('10..20')
    meval = m.exp.eval()
    assert meval == list(range(10, 21))


def test_expresions_messages():
    """
    Test sending messages to compound types
    """
    mm = metamodel_from_file(join(this_folder, 'expression.tx'), classes=custom_classes)

    m = mm.model_from_str('10..20 shuffle')
    meval = m.exp.eval()
    assert all([x in meval for x in range(10, 21)])

    m = mm.model_from_str('[1, 2, "some value"] shuffle')
    meval = m.exp.eval()
    assert all([x in meval for x in [1, 2, "some value"]])

    m = mm.model_from_str('10..20 choose')
    meval = m.exp.eval()
    assert meval in range(10, 21)

    m = mm.model_from_str('[1, 2, "some value"] choose')
    meval = m.exp.eval()
    assert meval in [1, 2, 'some value']


def test_expressions_if_expression():
    """
    Testing if expression of the form:
    <some val if cond true> if <condition> else <some other value>
    """
    mm = metamodel_from_file(join(this_folder, 'expression.tx'), classes=custom_classes)

    m = mm.model_from_str('1 if 2 < 2 else 3')
    meval = m.exp.eval()
    assert meval == 3

    m = mm.model_from_str('1 if 2 == 2 else 3')
    meval = m.exp.eval()
    assert meval == 1

    m = mm.model_from_str('2 > 3 or 8 < 9 if 2 == 2 else 3 < 2')
    meval = m.exp.eval()
    assert meval is True

    m = mm.model_from_str('some_symbol if 2 == 2 else "some string"')
    meval = m.exp.eval()
    assert type(meval) is Symbol and meval.name == 'some_symbol'

    m = mm.model_from_str('some_symbol if 2 != 2 else "some string"')
    meval = m.exp.eval()
    assert meval == 'some string'


def test_string_interpolation():
    mm = metamodel_from_file(join(this_folder, 'variables.tx'), classes=custom_classes)

    m = mm.model_from_str('''
    a = 5
    b = "some string"
    Pi = 3.14

    "this is {a} interpolation {b} {Pi}"
    ''')
    assert m.exp.eval() == 'this is 5 interpolation some string 3.14'

    with pytest.raises(PyFliesException, match=r'.*Undefined variable.*'):
        m = mm.model_from_str('''
        a = 5

        "this is {a} interpolation {b}"
        ''')
        m.exp.eval()

    with pytest.raises(PyFliesException, match=r'.*Undefined variable.*'):
        m = mm.model_from_str('''
        "this is {a} interpolation {b}"
        ''')
        m.exp.eval()


def test_expression_reduction():
    """
    Test that expression is reduced to its minimal constituents.
    This is an optimization measure and also helps with expression analysis.
    """

    mm = metamodel_from_file(join(this_folder, 'expression.tx'), classes=custom_classes)

    m = mm.model_from_str('25')
    assert type(m.exp) is OrExpression
    assert type(m.exp.reduce()) is BaseValue
    assert m.exp.eval() == 25

    m = mm.model_from_str('25 + 12')
    assert type(m.exp) is OrExpression
    assert type(m.exp.reduce()) is AdditiveExpression
    assert m.exp.eval() == 37

    m = mm.model_from_str('[1, 2, [\'some string\', 3.4, true], 5..7]')
    assert type(m.exp) is OrExpression
    mred = m.exp.reduce()
    assert type(mred) is List
    assert type(mred[0]) is BaseValue
    assert type(mred[2]) is List
    assert type(mred[3]) is Range
    assert type(mred[2][0]) is String
    assert type(mred[2][1]) is BaseValue
    assert m.exp.eval() == [1, 2, ['some string', 3.4, True], [5, 6, 7]]


def test_variables():
    """
    Test variables definition (assignments) and expression evaluation with
    variables.
    """
    mm = metamodel_from_file(join(this_folder, 'variables.tx'), classes=custom_classes)

    m = mm.model_from_str('''
    a = 5
    b = "some string"
    a + 10
    ''')
    assert m.exp.eval() == 15

    m = mm.model_from_str('''
    a = 5
    b = 45.5
    a / 2 + 10.25 * 6
    ''')
    assert m.exp.eval() == 64

    # Unexisting variables
    with pytest.raises(PyFliesException, match=r'.*Undefined variable.*'):
        m = mm.model_from_str('''
        a = 5
        2 + b - 10.25 * 6
        ''')
        m.exp.eval()

    with pytest.raises(PyFliesException, match=r'.*Undefined variable.*'):
        m = mm.model_from_str('''
        2 + b - 10.25 * 6
        ''')
        m.exp.eval()

    # Undefined variable standing on its own (e.g. without taking part of any
    # operations) is called symbol. It represent itself.
    m = mm.model_from_str('some_symbol')
    meval = m.exp.eval()
    assert type(meval) is Symbol
    assert meval.name == 'some_symbol'


def test_stimuli_definition():

    mm = metamodel_from_file(join(this_folder, 'stimuli.tx'), classes=custom_classes)

    m = mm.model_from_str('at 100 circle(position 0, radius 20) for 200')
    stim = m.stimuli[0]
    assert stim.duration == 200
    assert stim.at.time == 100
    assert not stim.record
    assert stim.stimulus.name == 'circle'
    assert stim.stimulus.params[0].name == 'position'
    assert stim.stimulus.params[0].value.eval() == 0
    assert stim.stimulus.params[1].name == 'radius'
    assert stim.stimulus.params[1].value.eval() == 20

    # Time can relative to the start of the previous stimulus
    m = mm.model_from_str('at .+100 circle(position 0, radius 20) for 200')
    stim = m.stimuli[0]
    assert stim.at.time == 100
    assert stim.at.relative_op == '+'
    assert stim.at.start_relative

    # Time can relative to the end of the previous stimulus
    m = mm.model_from_str('at +100 circle(position 0, radius 20) for 200')
    stim = m.stimuli[0]
    assert stim.at.time == 100
    assert stim.at.relative_op == '+'
    assert not stim.at.start_relative

    # If not given, by default it is the same as the start of the previous
    # E.g. `at .`
    m = mm.model_from_str('circle(position 0, radius 20) for 200')
    stim = m.stimuli[0]
    assert stim.at.time == 0
    assert stim.at.relative_op == '+'
    assert stim.at.start_relative

    # If duration is not given it is assumed that stimulus should be shown
    # until the end of the trial
    m = mm.model_from_str('at 100 circle(position 0, radius 20)')
    stim = m.stimuli[0]
    assert stim.duration == 0

    m = mm.model_from_str('at 100 record')
    stim = m.stimuli[0]
    assert stim.duration == 0
    assert stim.record
    assert stim.at.time == 100

    # If both recording and stimulus are defined at the same time it is parsed
    # as two statements: first will start recording at 100
    # and the second is circle stimuli for 200
    m = mm.model_from_str('at 100 record circle(position 0, radius 20) for 200')
    assert len(m.stimuli) == 2
    assert m.stimuli[0].record and not m.stimuli[1].record
    assert m.stimuli[1].at.time == 0 and m.stimuli[1].stimulus.name == 'circle'


def test_conditions_table():

    mm = metamodel_from_file(join(this_folder, 'cond_table.tx'), classes=custom_classes)

    m = mm.model_from_str('''
        {
            | position | color | congruency  | response |
            |----------+-------+-------------+----------|
            | left     | green | congruent   | left     |
            | left     | red   | incongruent | right    |
            | right    | green | incongruent | left     |
            | right    | red   | congruent   | right    |
        }
    ''')
    assert m.t[0].t.variables == ['position', 'color', 'congruency', 'response']
    # We have 4 rows in the table
    assert len(m.t[0].t.condition_specs) == 4
    c = m.t[0].t.condition_specs[1]
    red = c.var_exps[1].eval()  # This evaluates to symbol `red`
    assert type(red) is Symbol
    assert red.name == 'red'


def test_conditions_table_expansion():
    """
    Test that iterations and loops are expanded properly.
    """

    classes = list(custom_classes)

    class CTable(CustomClass):
        def expand(self):
            self.t.expand()

    classes.append(CTable)
    mm = metamodel_from_file(join(this_folder, 'cond_table.tx'), classes=classes)

    m = mm.model_from_str('''
        positions = [left, right]
        colors = [green, red]

        {   // Unexpanded table with loops
            | position       | color       | response  |
            |----------------+-------------+-----------|
            | positions loop | colors loop | positions |
        }

        {   // This should be the result of expansion
            | position | color | response |
            |----------+-------+----------|
            | left     | green | left     |
            | left     | red   | right    |
            | right    | green | left     |
            | right    | red   | right    |
        }

        {   // Lets change order a bit. Make color top loop and position inner loop
            | color       | response  | position       |
            |-------------+-----------+----------------|
            | colors loop | positions | positions loop |
        }

        {   // This should be the result of expansion
            | color | response | position |
            |-------+----------+----------|
            | green | left     | left     |
            | green | right    | right    |
            | red   | left     | left     |
            | red   | right    | right    |
        }
    ''')
    for i in range(4):
        m.t[i].expand()

    # position and color will loop making color a nested loop of the position
    # response will cycle
    assert m.t[0].t.conditions == m.t[1].t.conditions

    # In this case position is inner loop of color. response still cycles.
    assert m.t[2].t.conditions == m.t[3].t.conditions


def test_conditions_table_condition_variable_reference():
    """
    Test that references to condition variables are evaluated properly during
    table expansion.
    """

    mm = metamodel_from_file(join(this_folder, 'cond_table.tx'), classes=custom_classes)

    m = mm.model_from_str('''
        positions = [left, right]
        colors = [green, red]

        {
        | position       | color       | congruency                                        | response  |
        |----------------+-------------+---------------------------------------------------+-----------|
        | positions loop | colors loop | congruent if reponse == position else uncongruent | positions |
        }
    ''')
