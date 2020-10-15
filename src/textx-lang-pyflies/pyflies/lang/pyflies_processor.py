from textx import TextXSemanticError, get_children_of_type
# from pyflies.generators import generator_names
from .common import ExpressionElement, reduce_exp


def processor(model, metamodel):

    # Reduce all expressions
    reduce_exp(model)

    # Evaluate model-level variables
    model.eval()

    # Create default instances of all test component with default param values
    for test in get_children_of_type("TestType", model):
        # Evaluate test scope variables
        test.eval()
        # Create default components - useful for pre-init for some targets
        test.instantiate_default_components()

    # Evaluate flow
    # Result will be a nested lists of evaluated test/screen instances


    # Expand tables and calc phases
    for table in get_children_of_type('ConditionsTable', model):
        table.expand()
        table.calc_phases()
