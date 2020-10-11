import pytest
import os
from os.path import join, dirname, abspath
from textx import metamodel_from_file, metamodel_for_language, scoping, TextXSemanticError
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
    t = m.routines[0].table

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
        param abs_param: int
    }

    component test_comp extends abs_comp
    """
    This is test component
    """
    {
        // First param don't have a default value and thus is mandatory
        param first_param: string

        // Second param has default value and thus is optional
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


def test_components_param_type_referencing_and_default():
    """
    Test that component instances can reference component and param types and
    that if param is not set the default value will be applied.
    """
    mm = metamodel_for_language('pyflies')

    m = mm.model_from_file(join(this_folder, 'test_component_parameters.pf'))

    t = m.routines[0]

    comp_time = t.components_cond[0].comp_times[0]


    comp_type = comp_time.component.type
    assert comp_type.name == 'cross'


    # Check default values for parameters
    table = t.table
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
        m = mm.model_from_file(join(this_folder, 'test_component_parameters_wrong.pf'))
