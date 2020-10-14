from .lang.common import Symbol


def resolve_params(model, param_dict):
    """
    Find all unresolved symbols for component param values in the experiment
    model and replace with values from the provided param_dict.  Collect and
    return all that can't be replaced to issue a warning to the user.
    """
    visited = set()
    unresolved = set()
    def recursive_resolve(obj):
        if id(obj) in visited:
            return
        visited.add(id(obj))
        try:
            attrs = vars(obj).values()
        except TypeError:
            if isinstance(obj, list):
                attrs = obj
            elif isinstance(obj, dict):
                attrs = obj.values()
            else:
                return

        for attr in attrs:
            if attr.__class__.__name__ == 'ComponentParamInst':
                if type(attr.value) is Symbol:
                    if attr.value.name in param_dict:
                        attr.value = param_dict[attr.value.name]
                    else:
                        unresolved.add(attr.value.name)
            recursive_resolve(attr)
    recursive_resolve(model)

    return unresolved
