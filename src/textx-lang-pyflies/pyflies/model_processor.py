from textx import TextXSemanticError, get_children_of_type
from textx.const import MULT_ONE, MULT_OPTIONAL
# from pyflies.generators import generator_names
from .model import ExpressionElement


def processor(model, metamodel):

    def reduce(obj):
        """
        Descends down the containment tree and reduce all expressions.
        """
        cls = obj.__class__
        if hasattr(cls, '_tx_attrs'):
            for attr_name, attr in obj._tx_attrs.items():
                # Follow only attributes with containment semantics
                if attr.cont:
                    if attr.mult in (MULT_ONE, MULT_OPTIONAL):
                        new_elem = getattr(obj, attr_name)
                        if new_elem is not None:
                            if isinstance(new_elem, ExpressionElement):
                                reduced = new_elem.reduce()
                                setattr(obj, attr_name, reduced)
                            else:
                                reduce(new_elem)
                    else:
                        new_elem_list = getattr(obj, attr_name)
                        if new_elem_list:
                            for idx, new_elem in enumerate(new_elem_list):
                                if isinstance(new_elem, ExpressionElement):
                                    reduced = new_elem.reduce()
                                    new_elem_list[idx] = reduced
                                else:
                                    reduce(new_elem)

    # Reduce all expressions
    reduce(model)

    # Evaluate model-level variables
    model.eval()

    # Expand tables and calc phases
    for table in get_children_of_type('ConditionsTable', model):
        table.expand()
        table.calc_phases()
