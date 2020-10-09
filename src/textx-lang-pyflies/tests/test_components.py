import pytest
import os
from os.path import join, dirname, abspath
from textx import metamodel_from_file, metamodel_for_language, scoping
from pyflies.lang.common import classes as common_classes
from pyflies.lang.pyflies import classes as model_classes
from .common import get_meta


this_folder = dirname(abspath(__file__))


def test_components_variable_assignments():
    """
    Test that variables defined in the trial block are evaluated during table
    expansion for each table row.
    """

    mm = get_meta('pyflies.tx', classes=model_classes)

    m = mm.model_from_file(join(this_folder, 'TestModel.pf'))

    # Get expanded table
    t = m.routines[0].table.expanded

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
