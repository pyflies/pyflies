import pytest
from os.path import join, dirname, abspath
from textx import metamodel_for_language

from pyflies.lang.common import (ModelElement, Symbol, BaseValue,
                                 AdditiveExpression, List, String, Range)
from pyflies.scope import ScopeProvider
from pyflies.exceptions import PyFliesException
from pyflies.lang.pyflies import classes as model_classes
from .common import get_meta, Model


this_folder = dirname(abspath(__file__))


class CTable(ModelElement, ScopeProvider):
    pass


def test_time_references():
    """Test for pyflies time references"""

    mm = get_meta('timeref.tx')

    # Plain
    ref = mm.model_from_str('10').ref.eval()
    assert ref.relative_op is None
    assert not ref.start_relative
    assert ref.time == 10

    # Positive relative from previous end
    ref = mm.model_from_str('+10').ref.eval()
    assert ref.relative_op == '+'
    assert ref.time == 10
    assert not ref.start_relative

    # Negative relative from previous end
    ref = mm.model_from_str('-10').ref.eval()
    assert ref.relative_op == '-'
    assert ref.time == 10

    # Positive relative from previous start
    ref = mm.model_from_str('.+10').ref.eval()
    assert ref.relative_op == '+'
    assert ref.start_relative
    assert ref.time == 10

    # Time reference can be an integer expression
    ref = mm.model_from_str('.+10 + 3 * 2').ref.eval()
    assert ref.relative_op == '+'
    assert ref.start_relative
    assert ref.time == 16


def test_expressions_arithmetic():
    """
    Test Pyflies arithmetic expressions.
    """

    mm = get_meta('expression.tx')

    exp = mm.model_from_str('2 + 3 * 2 * 3 / 5 - 1')
    assert exp.exp.eval() == 4.6


def test_expressions_comparison_boolean():
    """
    Test Pyflies boolean expressions.
    """

    mm = get_meta('expression.tx')

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
    mm = get_meta('expression.tx')

    m = mm.model_from_str('[1, 2, ["some string", 4.5], 3]')
    meval = m.exp.eval()
    assert meval == [1, 2, ['some string', 4.5], 3]

    # Test that a single list element is an evaluatable expression
    assert m.exp[0].eval() == 1

    m = mm.model_from_str('10..20')
    meval = m.exp.eval()
    assert meval == list(range(10, 21))


def test_expresions_messages():
    """
    Test sending messages to compound types
    """
    mm = get_meta('expression.tx')

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
    mm = get_meta('expression.tx')

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

    mm = get_meta('variables.tx')

    m = mm.model_from_str('''
    a = 5
    b = "some string"
    Pi = 3.14

    "this is {{a}} interpolation {{b}} {{Pi}}"
    ''')
    assert m.exp.eval() == 'this is 5 interpolation some string 3.14'

    with pytest.raises(PyFliesException, match=r'.*Undefined variable.*'):
        m = mm.model_from_str('''
        a = 5

        "this is {{a}} interpolation {{b}}"
        ''')
        m.exp.eval()

    with pytest.raises(PyFliesException, match=r'.*Undefined variable.*'):
        m = mm.model_from_str('''
        "this is {{a}} interpolation {{b}}"
        ''')
        m.exp.eval()


def test_expression_reduction():
    """
    Test that expressions are reduced to their minimal constituents.
    This is an optimization measure and also helps with expression analysis.
    """

    mm = get_meta('expression.tx')

    m = mm.model_from_str('25')
    assert type(m.exp) is BaseValue
    assert m.exp.eval() == 25

    m = mm.model_from_str('25 + 12')
    assert type(m.exp) is AdditiveExpression
    assert m.exp.eval() == 37

    m = mm.model_from_str('[1, 2, [\'some string\', 3.4, true], 5..7]')
    mred = m.exp
    assert type(mred) is List
    assert type(mred[0]) is BaseValue
    assert type(mred[2]) is List
    assert type(mred[3]) is Range
    assert type(mred[2][0]) is String
    assert type(mred[2][1]) is BaseValue
    assert m.exp.eval() == [1, 2, ['some string', 3.4, True], [5, 6, 7]]


@pytest.mark.parametrize('exp, rep',
                         [
                             ('25', '25'),
                             ('25 + 12 +3 * 4 /3', '25 + 12 + 3 * 4 / 3'),
                             ('true or False and a and not 3 >= 5.4< 3',
                              'True or False and a and not 3 >= 5.4 < 3'),
                             ('1..5 loop', '1..5 loop'),
                             ('1..5 shuffle', '1..5 shuffle'),
                             ('[1, 2, 3] shuffle', '[1, 2, 3] shuffle'),
                             ('a if 3 > 5 and b else c', 'a if 3 > 5 and b else c'),
                         ])
def test_string_representation(exp, rep):

    mm = get_meta('expression.tx')
    assert str(mm.model_from_str(exp).exp.reduce()) == rep


def test_variables():
    """
    Test variables definition (assignments) and expression evaluation with
    variables.
    """
    mm = get_meta('variables.tx')

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


def test_scope_providers():
    """
    Scope providers are object which provides scope for variable definition.
    Variable can be defined in any child element of the scope provider.  Scope
    providers provide means to evaluate variable values using postponing for
    forward references, detecting circular references and using variable values
    from parent scope providers.
    """
    class SProvider(ModelElement, ScopeProvider):
        pass

    mm = get_meta('scope.tx', classes=model_classes + [Model, SProvider])

    m = mm.model_from_str('''
    a = 1..10 choose
    b = 5 + a
    {
      // We can use outer scope vars in variable definition
      c = 3 + b

      // And in expressions, here can use `c` after evaluation
      //
      a + c
    }
    a + b
    ''')

    # Model level evaluation is done by model processor
    # Wee need to evaluate only inner scope
    assert not m.inner_scope.var_vals
    m.inner_scope.eval()
    assert m.inner_scope.var_vals

    a, b = m.var_vals['a'], m.var_vals['b']
    assert b == 5 + a
    assert m.exp.eval() == a + b
    assert 'c' not in m.var_vals
    assert 'c' in m.inner_scope.var_vals
    c = m.inner_scope.var_vals['c']
    assert c == 3 + b
    assert m.inner_scope.exp.eval() == a + c

    m = mm.model_from_str('''
    a = 2
    {
      // We can use outer scope vars in variable definition
      c = 3 + a

      // And in expressions, here can use `c` after evaluation
      //
      a + c
    }
    // But `c` is not visible here
    a + c
    ''')

    m.inner_scope.eval()
    with pytest.raises(PyFliesException, match=r'Undefined variable "c"'):
        m.exp.eval()

    # We can use forward referencing
    m = mm.model_from_str('''
    a = b choose
    b = 1..10
    a + 100
    ''')
    assert m.var_vals['a'] + 100 == m.exp.eval()


def test_conditions_table():

    mm = metamodel_for_language('pyflies')

    m = mm.model_from_str('''
    test Test {
        | position | color | congruency  | response |
        |----------+-------+-------------+----------|
        | left     | green | congruent   | left     |
        | left     | red   | incongruent | right    |
        | right    | green | incongruent | left     |
        | right    | red   | congruent   | right    |
    }
    flow {
        execute Test
    }
    ''')

    # We have 4 rows in the table
    assert m.routine_types[0].table_spec.variables == ['position', 'color',
                                                       'congruency', 'response']

    red = m.flow.insts[0].table[1][1]
    assert type(red) is Symbol
    assert red.name == 'red'


def test_conditions_table_expansion():
    """
    Test that iterations and loops are expanded properly.
    """

    mm = metamodel_for_language('pyflies')

    m = mm.model_from_str('''
    positions = [left, right]
    colors = [green, red]

    test First {
        // Unexpanded table with loops
        | position       | color       | response  |
        |----------------+-------------+-----------|
        | positions loop | colors loop | positions |
    }

    test First_exp {

        // This should be the result of expansion
        | position | color | response |
        |----------+-------+----------|
        | left     | green | left     |
        | left     | red   | right    |
        | right    | green | left     |
        | right    | red   | right    |
    }

    test Second {
        // Lets change order a bit. Make color top loop and position inner loop
        | color       | response  | position       |
        |-------------+-----------+----------------|
        | colors loop | positions | positions loop |
    }

    test Second_exp {
        // This should be the result of expansion
        | color | response | position |
        |-------+----------+----------|
        | green | left     | left     |
        | green | right    | right    |
        | red   | left     | left     |
        | red   | right    | right    |
    }

    flow {
        execute First
        execute First_exp
        execute Second
        execute Second_exp
    }
    ''')

    # position and color will loop making color a nested loop of the position
    # response will cycle
    assert m.flow.insts[0].table == m.flow.insts[1].table

    # In this case position is inner loop of color. response still cycles.
    assert m.flow.insts[2].table == m.flow.insts[3].table


def test_conditions_table_no_loop_expansion():
    """
    Test that iterations without loops are expanded properly.
    """

    mm = metamodel_for_language('pyflies')

    m = mm.model_from_str('''
    positions = [left, right]
    colors = [green, red, blue]

    test Test {
        // Unexpanded table with iterations only
        | position | color  | response  |
        |----------+--------+-----------|
        | (0, 10)  | colors | positions |
    }
    flow {
        execute Test
    }
    ''')
    assert str(m.flow.insts[0].table) == \
        '''
| position | color | response |
|----------+-------+----------|
| (0, 10)  | green | left     |
| (0, 10)  | red   | right    |
| (0, 10)  | blue  | left     |

        '''.strip()


def test_conditions_table_no_loop_no_sequence_expansion():
    """
    Test that iterations without loops and sequences are expanded properly.
    """

    mm = metamodel_for_language('pyflies')

    m = mm.model_from_str('''
    test Test {
        // Unexpanded table without loops and sequences
        | position | color | response |
        |----------+-------+----------|
        | (0, 10)  | 2 + 4 | 6 - 2    |
        | (0, 10)  | 2 + 5 | 6 - 2    |
    }
    flow { execute Test }
    ''')
    assert str(m.flow.insts[0].table) == \
        '''
| position | color | response |
|----------+-------+----------|
| (0, 10)  | 6     | 4        |
| (0, 10)  | 7     | 4        |

        '''.strip()


def test_condition_table_if_expression_loop_model_param():
    """
    Test that if expression in table loop is correctly evaluated in the context
    of model parameters.  Can be used for counterbalancing.
    """
    mm = metamodel_for_language('pyflies')

    mm_str = r'''
    positions = [left, right] if group == 'A' else [right, left]

    test Test {

        | position       | range     | plain |
        |----------------+-----------+-------|
        | positions loop | 1..2 loop | 1     |
    }
    flow {execute Test}
    '''

    m = mm.model_from_str(mm_str, group='A')

    assert str(m.flow.insts[0].table) == r'''
| position | range | plain |
|----------+-------+-------|
| left     | 1     | 1     |
| left     | 2     | 1     |
| right    | 1     | 1     |
| right    | 2     | 1     |
    '''.strip()

    m = mm.model_from_str(mm_str, group='B')

    assert str(m.flow.insts[0].table) == r'''
| position | range | plain |
|----------+-------+-------|
| right    | 1     | 1     |
| right    | 2     | 1     |
| left     | 1     | 1     |
| left     | 2     | 1     |
    '''.strip()


def test_conditions_table_str_representation():
    """
    Test that tables are properly formatted when converted to string
    representation.
    """

    mm = metamodel_for_language('pyflies')

    m = mm.model_from_str('''
    positions = [left, right]
    colors = [green, red]

    test Test {

        | position       | color       | congruency                                         | response  |
        |----------------+-------------+----------------------------------------------------+-----------|
        | positions loop | colors loop | congruent if response == position else incongruent | positions |
    }
    flow {execute Test}
    ''')  # noqa

    assert m.routine_types[0].table_spec.to_str() == \
        '''
| position       | color       | congruency                                         | response  |
|----------------+-------------+----------------------------------------------------+-----------|
| positions loop | colors loop | congruent if response == position else incongruent | positions |
        '''.strip()  # noqa

    assert str(m.flow.insts[0].table) == \
        '''
| position | color | congruency  | response |
|----------+-------+-------------+----------|
| left     | green | congruent   | left     |
| left     | red   | incongruent | right    |
| right    | green | incongruent | left     |
| right    | red   | congruent   | right    |
        '''.strip()

    m = mm.model_from_str('''
    test Test {
        | position | order          |
        |----------+----------------|
        | order    | [1, 2, 3] loop |
    }
    flow {execute Test}
    ''')
    assert str(m.flow.insts[0].table) == '''
| position | order |
|----------+-------|
| 1        | 1     |
| 2        | 2     |
| 3        | 3     |
    '''.strip()


def test_conditions_table_condition_cyclic_reference():
    """
    Test that table expression with cyclic references raise exception.
    """

    mm = metamodel_for_language('pyflies')

    with pytest.raises(PyFliesException, match=r'Cyclic dependency.*'):
        mm.model_from_str('''
        test Test{
            | position | color    |
            |----------+----------|
            | color    | position |
        }
        flow {execute Test}
        ''')


def test_undefined_loop_variable():
    """
    Test that table expression with undefined loop variable raises exception.
    """

    mm = metamodel_for_language('pyflies')

    with pytest.raises(PyFliesException, match=r'Undefined variable "myvar"'):
        mm.model_from_str('''
        test Test{
            | undefined_var |
            |---------------|
            | myvar loop    |
        }
        flow {execute Test}
        ''')


def test_conditions_table_phases_evaluation():
    """
    Test that evaluated table has attached appropriate components specifications
    for each trial phase.
    """
    mm = metamodel_for_language('pyflies')

    m = mm.model_from_str('''
        positions = [left, right]
        colors = [green, red]

        test Example {
              | position       | color       | response  |
              |----------------+-------------+-----------|
              | positions loop | colors loop | positions |

              fix -> cross() for 200..500 choose
              exec -> circle(position position, color color) for 300..700 choose
              error and color == green -> sound(freq 300)
              error -> sound(freq 500)
              correct -> sound(freq 1000)
        }
        flow { execute Example }
    ''')

    t = m.flow.insts[0].table
    for trial in range(4):
        # fix
        s = t[trial].ph_fix[0]
        assert s.component.name == 'Example_cross'
        assert s.at == 0
        assert 200 <= s.duration <= 500

        # exec
        st = t[trial].ph_exec[0]
        assert st.component.name == 'Example_circle'
        assert st.at == 0
        assert 300 <= st.duration <= 700

        # error
        st = t[trial].ph_error[0]
        assert st.component.name == 'Example_sound' \
            if t[trial][1].name == 'green' else 'Example_sound_2'
        # Frequencies are 300 when color is green and 500 otherwise
        assert st.component.params[0].value == 300 if t[trial][1].name == 'green' else 500

        # Correct
        st = t[trial].ph_correct[0]
        assert st.component.name == 'Example_sound_3'
        assert st.component.params[0].name == 'freq'
        assert st.component.params[0].value == 1000

    # Parameters evaluation
    st = t[0].ph_exec[0]
    assert st.component.params[0].value == 'left'
    assert st.component.params[1].value == 'green'


def test_experiment_structure():
    """
    Test full experiment structure
    """

    mm = metamodel_for_language('pyflies')

    m = mm.model_from_file(join(this_folder, 'TestModel.pf'))
    assert len(m.routine_types) == 3
    assert m.routine_types[1].__class__.__name__ == 'ScreenType'
    assert m.description == 'Model for testing purposes.\n'
    assert len(m.flow.block.statements) == 4

    # Practice run
    ptest = m.flow.block.statements[1]
    assert [x.value.eval() for x in ptest.what.args if x.name == 'practice'][0]
    assert ptest.times is None and ptest._with is None

    # Block repeat
    rtest = m.flow.block.statements[2]
    assert rtest.times.eval() == 3
    assert not rtest.what.random

    # Inner test
    itest = rtest.what.statements[1]
    assert itest.times.eval() == 5

    # Random repeat
    rtest = m.flow.block.statements[3]
    assert rtest.times.eval() == 2
    assert rtest.what.random


def test_target_configuration():
    """
    Test that target configuration is parsed correctly.
    """
    mm = metamodel_for_language('pyflies')

    m = mm.model_from_file(join(this_folder, 'TestModel.pf'))

    t = m.targets[0]
    assert t.settings[0].value == 'left'
    assert t.settings[2].value == 5

    assert t.settings[4].name == 'resolution'
    v = t.settings[4].value.value
    assert v.x == 1024
    assert v.y == 768


def test_flow_instances_expansion():
    """
    Test that flow instances are correctly created.
    """
    mm = metamodel_for_language('pyflies')
    m = mm.model_from_file(join(this_folder, 'TestModel.pf'))

    assert len(m.flow.insts) == 2 + 3 * 6 + 2 * 3

    # screen duration
    assert m.flow.insts[0].duration == 5000

    # Test arguments
    # This test has practice = True
    assert m.flow.insts[1].table[0].ph_fix[0].duration == 100
    # This test has practice = False
    assert m.flow.insts[3].table[0].ph_fix[0].duration == 500


def test_experiment_time_calculations():
    """
    Test full experiment relative/absolute time calculations.
    """

    mm = metamodel_for_language('pyflies')

    m = mm.model_from_file(join(this_folder, 'TestModel.pf'))

    # Get expanded table
    t = m.flow.insts[1].table

    trial = t[0]
    comps = trial.ph_exec
    assert comps[1].at == 150
    assert comps[2].at == 300
    assert comps[3].at == 650
    assert comps[4].at == 550


def test_routine_parameters():
    """
    Test that screens and tests can accept parameters.
    """
    mm = metamodel_for_language('pyflies')

    m = mm.model_from_file(join(this_folder, 'test_routine_parameters.pf'))

    # Test that screen is rendered
    assert m.flow.insts[0].content.strip() == r'''
    You will be presented with images of houses
    Here is a number -> 5
    '''.strip()

    # We have test and a screen repeated 3 times
    assert len(m.flow.insts) == 7
    assert m.flow.insts[1].table[5][0] == 6
    assert m.flow.insts[1].table[5][1] == 'houses/6.png'

    assert m.flow.insts[6].content.strip() == r'''
    Block 3 is over.
    Take a short break
    '''.strip()


def test_repeat_with():
    """
    test `repeat` with a `with` table
    """
    mm = metamodel_for_language('pyflies')
    m = mm.model_from_file(join(this_folder, 'test_repeat_with.pf'))

    # We have one screen and one test for each row of the repeat/with table
    assert len(m.flow.insts) == 4

    assert m.flow.insts[1].table[0][1] == 'houses/1.png'
    assert m.flow.insts[3].table[0][1] == 'faces/1.png'

    assert m.flow.insts[0].content.strip() == r'''
       You will be presented with images of houses.
       Here is 11.0.
    '''.strip()

    assert m.flow.insts[2].content.strip() == r'''
       You will be presented with images of faces.
       Here is 8.
    '''.strip()


def test_jinja_filters_in_screens():
    """
    Test that Jinja filters are working as expected
    """


def test_crlf_line_endings():
    """
    Test parsing of files using CRLF line endings.
    """
    mm = metamodel_for_language('pyflies')
    m = mm.model_from_file(join(this_folder, 'test_newlines_crlf.pf'))

    assert len(m.flow.insts) == 2
