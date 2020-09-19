import pytest
from os.path import join, dirname, abspath
from textx import metamodel_from_file, TextXSyntaxError

from pyflies.custom_classes import custom_classes
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
