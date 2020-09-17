from os.path import join, dirname, abspath
from textx import metamodel_from_file

from pyflies.expressions import custom_exp_classes


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

    exp = mm.model_from_str('2 + 3 * 2 * 3 / 5 - 1')
    print(exp.exp.eval())
    import pdb; pdb.set_trace()



