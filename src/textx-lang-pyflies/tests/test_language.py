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


def test_expressions():
    """
    Test Pyflies expressions.
    """

    mm = metamodel_from_file(join(this_folder, 'expression.tx'), classes=custom_exp_classes)

    # Basic arithmetic
    exp = mm.model_from_str('2 + 3 * 2 * 3 / 5 - 1')
    assert exp.exp.eval() == 4.6

    # comparisons and booleans
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

