from textx import TextXSemanticError, get_children_of_type
# from pyflies.generators import generator_names
from .common import ExpressionElement, reduce_exp


def processor(model, metamodel):

    # Reduce all expressions
    reduce_exp(model)

    # Evaluate model-level variables
    model.eval()

    # Expand tables and calc phases
    for table in get_children_of_type('ConditionsTable', model):
        table.expand()
        table.calc_phases()
