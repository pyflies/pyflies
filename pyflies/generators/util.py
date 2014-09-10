from random import sample


def flatten_experiment(model):
    """
    Returns flatten list of experiment elements where randomize
    blocks are properly randomized.

    Args:
        model(pyFlies model)
    """

    elements = model.experiment.elements

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
