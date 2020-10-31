from textx import get_children_of_type
# from pyflies.generators import generator_names
from .common import reduce_exp


def processor(model, metamodel):

    # Reduce all expressions
    reduce_exp(model)

    # Evaluate model-level variables
    context = dict(model._tx_model_params)
    model.eval(context)

    # Create default instances of all test component with default param values
    for test in get_children_of_type("TestType", model):
        # Evaluate test scope variables
        test.eval(context)
        # Create default components - useful for pre-init for some targets
        test.instantiate_default_components()

    # Evaluate flow
    # Result will be model.flow.insts list with ScreenInst/TestInst
    if hasattr(model, 'flow') and model.flow:
        model.flow.eval(context)
