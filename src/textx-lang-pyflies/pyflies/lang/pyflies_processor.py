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
    # Result will be model.flow.insts list with ScreenInst/TestInst
    if hasattr(model, 'flow') and model.flow:
        model.flow.eval()
