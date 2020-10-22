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

        def map_symbol(comp_type, symbol):
            """
            Map the given symbol to the value from the settings.  Check first
            for component specific mapping.
            """
            comp_val = '{}.{}'.format(comp_type, symbol.name)
            if comp_val in param_dict:
                return param_dict[comp_val]
            elif symbol.name in param_dict:
                return param_dict[symbol.name]
            else:
                unresolved.add(symbol.name)

        def resolve_value(comp_type, param):
            if type(param.value) is list:
                new_values = []
                for e in param.value:
                    if type(e) is Symbol:
                        new_value = map_symbol(comp_type, e)
                        new_values.append(new_value if new_value is not None else e)
                param.value = new_values

            if type(param.value) is Symbol:
                new_value = map_symbol(comp_type, param.value)

                if new_value is not None:
                    param.value = new_value

        for attr in attrs:
            if attr.__class__.__name__ == 'ComponentParamInst':
                comp_type = attr.spec.parent.type.name
                resolve_value(comp_type, attr)
            else:
                recursive_resolve(attr)
    recursive_resolve(model)

    return unresolved
