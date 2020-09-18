import pytest
from os.path import join, dirname, abspath
from textx import metamodel_from_file

from pyflies.expressions import custom_exp_classes
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

    mm = metamodel_from_file(join(this_folder, 'expression.tx'), classes=custom_exp_classes)

    exp = mm.model_from_str('2 + 3 * 2 * 3 / 5 - 1')
    assert exp.exp.eval() == 4.6

def test_expressions_comparison_boolean():
    """
    Test Pyflies boolean expressions.
    """

    mm = metamodel_from_file(join(this_folder, 'expression.tx'), classes=custom_exp_classes)

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
    mm = metamodel_from_file(join(this_folder, 'expression.tx'), classes=custom_exp_classes)

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
    mm = metamodel_from_file(join(this_folder, 'expression.tx'), classes=custom_exp_classes)

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


def test_string_interpolation():
    mm = metamodel_from_file(join(this_folder, 'variables.tx'), classes=custom_exp_classes)

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


def test_variables():
    """
    Test variables definition (assignments) and expression evaluation with
    variables.
    """
    mm = metamodel_from_file(join(this_folder, 'variables.tx'), classes=custom_exp_classes)

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


def test_simuli_definition():

    mm = metamodel_from_file(join(this_folder, 'stimuli.tx'), classes=custom_exp_classes)

    m = mm.model_from_str('at 100 circle(position 0, radius 20) for 200')
    stim = m.stimuli[0]
    assert stim.duration == 200
    assert stim.at.time == 100
    assert stim.stimulus.name == 'circle'
    assert stim.stimulus.params[0].name == 'position'
    assert stim.stimulus.params[0].value.eval() == 0
    assert stim.stimulus.params[1].name == 'radius'
    assert stim.stimulus.params[1].value.eval() == 20

    m = mm.model_from_str('at 100 record')
    stim = m.stimuli[0]
    assert stim.duration == 0
    assert stim.record
    assert stim.at.time == 100
