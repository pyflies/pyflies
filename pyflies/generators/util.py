from random import sample
import re


def flatten_structure(model):
    """
    Returns flatten list of experiment elements where randomize
    blocks are properly randomized.

    Args:
        model(pyFlies model)
    """

    elements = model.structure.elements

    def _flatten(elements):
        instances = []
        for e in elements:
            if e.__class__.__name__ == "Sequence":
                instances.extend(_flatten(e.elements))
            elif e.__class__.__name__ == "Randomize":
                # Randomize contained elements
                instances.extend(_flatten(
                    sample(e.elements, len(e.elements))))
            else:
                # It must be an instance
                instances.append(e)
        return instances

    return _flatten(elements)


def python_module_name(name):
    """
    Converts given name str to a valid python module file name.
    Used to transform model name to valid model file in test
    code generators.

    Args:
        name(str)
    """
    return "%s.py" % re.sub(r'[^\w\.-]', '_', name.lower())
