import pytest
from os.path import join, dirname, abspath
from textx import metamodel_from_file, metamodel_for_language, TextXSemanticError
from pyflies.exceptions import PyFliesException
from pyflies.lang.common import classes as common_classes


this_folder = dirname(abspath(__file__))


def test_components_variable_assignments():
    """
    Test that variables defined in the trial block are evaluated during table
    expansion for each table row.
    """

    mm = metamodel_for_language('pyflies')

    m = mm.model_from_file(join(this_folder, 'TestModel.pf'))

    # Get expanded table
    t = m.flow.insts[1].table

    # Duration is 100 where direction is left, and 200 where direction is right
    trial = t[0]
    assert trial.var_vals['direction'].name == 'left'
    assert trial.ph_exec[2].duration == 100

    trial = t[2]
    assert trial.var_vals['direction'].name == 'right'
    assert trial.ph_exec[2].duration == 200


def test_component_specification():
    """
    Test component specification language
    """

    mm = metamodel_from_file(join(this_folder, 'components.tx'), classes=common_classes)

    model_str = r'''
    abstract component abs_comp
    """
    This component is used in inheritance
    """
    {
        param abs_param: int = 20
    }

    component test_comp extends abs_comp
    """
    This is test component
    """
    {
        param first_param: string = 'First param'

        param second_param: int = 5
        """
        Parameter description
        """

        // Third param can be of multiple types
        param multi_type: [int, string, symbol] = 10
    }
    '''

    model = mm.model_from_str(model_str)

    comp = model.comp_types[0]
    assert comp.abstract

    comp = model.comp_types[1]
    assert comp.param_types[1].description.strip() == 'Parameter description'
    assert comp.param_types[2].types == ['int', 'string', 'symbol']
    assert comp.param_types[2].default.eval() == 10
    assert comp.extends[0].param_types[0].default.eval() == 20


def test_component_timing_definition():

    mm = metamodel_for_language('pyflies')
    m = mm.model_from_file(join(this_folder, 'test_component_timing_definition.pf'))
    comp_times = m.routine_types[0].components_cond[0].comp_times

    # Time, duration and params can be expressions
    # at a + 100 c:circle(position 0, radius 5 + 15) for a + b * a + 140
    comp = comp_times[0].eval()
    assert comp.duration == 200
    assert comp.at == 110
    assert comp.component.name == 'TestModel_c1'
    assert comp.component.params[0].name == 'position'
    assert comp.component.params[0].value == 0
    assert comp.component.params[1].name == 'radius'
    assert comp.component.params[1].value == 20

    # Time can relative to the start of the previous component
    # at .+100 c:circle(position 0, radius 20) for 200
    comp = comp_times[1]
    assert comp.at.time.eval() == 100
    assert comp.at.relative_op == '+'
    assert comp.at.start_relative

    # Time can relative to the end of the previous component
    # at +100 c:circle(position 0, radius 20) for 200
    comp = comp_times[2]
    assert comp.at.time.eval() == 100
    assert comp.at.relative_op == '+'
    assert not comp.at.start_relative

    # If not given, by default it is the same as the start of the previous
    # E.g. `at .`
    # c:circle(position 0, radius 20) for 200
    comp = comp_times[3]
    assert comp.at.time.eval() == 0
    assert comp.at.relative_op == '+'
    assert comp.at.start_relative

    # If duration is not given it is assumed that component should be shown
    # until the end of the trial
    # at 100 c:circle(position 0, radius 20)
    comp = comp_times[4]
    assert comp.duration.eval() == 0


def test_components_param_type_referencing_and_default():
    """
    Test that component instances can reference component and param types and
    that if param is not set the default value will be applied.
    """
    mm = metamodel_for_language('pyflies')

    m = mm.model_from_file(join(this_folder, 'test_component_parameters.pf'))

    t = m.routine_types[0]

    comp_time = t.components_cond[0].comp_times[0]

    comp_type = comp_time.component.type
    assert comp_type.name == 'cross'

    # Check default values for parameters
    table = m.flow.insts[0].table
    trial = table.rows[0]
    comp_inst = trial.ph_exec[0].component
    assert comp_inst.spec.type.name == 'circle'
    # Given values
    assert comp_inst.radius == 100
    assert comp_inst.position.y == 40
    # Default values defined in abstract "visual" component
    assert comp_inst.color == '#ffffff'
    assert comp_inst.fillColor == '#ffffff'
    assert comp_inst.size == 20


def test_component_only_valid_param_can_be_referenced():
    """
    Test that only valid parameters from component definition can be referenced.
    """

    mm = metamodel_for_language('pyflies')

    with pytest.raises(TextXSemanticError, match=r'.*Unknown object "position".*'):
        mm.model_from_file(join(this_folder, 'test_component_parameters_wrong.pf'))


def test_default_component_instances():
    """
    Test that component instances with default param values are correctly collected.
    """
    mm = metamodel_for_language('pyflies')
    m = mm.model_from_file(join(this_folder, 'test_component_parameters.pf'))

    test = m.routine_types[0]
    assert test.components

    # Cross
    comp = test.components[0]
    assert comp.spec.type.name == 'cross'
    assert comp.name == 'TestModel_mycross'
    assert comp.params[0].spec.type.name == 'position'
    assert comp.params[0].is_constant

    # Circle
    comp = test.components[2]
    assert comp.spec.type.name == 'circle'
    assert comp.name == 'TestModel_target'
    assert not comp.params[0].is_constant
    # For params which depends on condition variables default value (defined in
    # the param type) will be used
    assert comp.params[0].value.x == 0
    assert comp.params[0].value.y == 0

    # Non-constant param with transitive reference to condition table
    comp = test.components[3]
    assert comp.name == 'TestModel_sound'
    assert comp.params[0].type.name == 'freq'
    assert not comp.params[0].is_constant

    # Constant parameter with transitive reference to local scope
    comp = test.components[4]
    assert comp.name == 'TestModel_sound_2'
    assert comp.params[0].type.name == 'freq'
    assert comp.params[0].is_constant
    assert comp.params[0].value == 123

    # Mouse target is referenced component
    comp = test.components[8]
    assert comp.name == 'TestModel_mouse'
    assert comp.params[0].name == 'target'
    assert comp.params[0].value == test.components[2]

    # Mouse target may be a list
    comp = test.components[9]
    assert comp.name == 'TestModel_mouse_2'
    assert comp.params[0].name == 'target'
    assert comp.params[0].value == [test.components[2], test.components[1]]


def test_trial_component_instances():
    """
    Test that component instances for each trial are correctly instantiated.
    """
    mm = metamodel_for_language('pyflies')
    m = mm.model_from_file(join(this_folder, 'test_trial_component_parameters.pf'))

    test = m.flow.insts[0]
    trial = test.table.rows[0]
    assert trial.ph_exec[0].component.params[1].value == 'left'
    assert trial.ph_exec[1].component.params[0].value.y == 50
    assert trial.ph_exec[2].component.params[0].value == 500

    trial = test.table.rows[1]
    assert trial.ph_exec[0].component.params[1].value == 'up'
    assert trial.ph_exec[2].component.params[0].value == 200


def test_component_name_must_be_unique():
    """
    Check that component name must be unique in the scope.
    """

    mm = metamodel_for_language('pyflies')

    # Condition variable with the same name
    with pytest.raises(PyFliesException, match=r'Cannot name component'):
        mm.model_from_file(join(this_folder, 'test_component_name_unique_1.pf'))

    # Component with the same name
    with pytest.raises(PyFliesException, match=r'Cannot name component'):
        mm.model_from_file(join(this_folder, 'test_component_name_unique_2.pf'))
