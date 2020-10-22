import sys
import inspect
from .common import classes as common_classes, ModelElement


class ComponentType(ModelElement):
    def does_extend(self, name):
        visited = set()

        def _does_extend(obj, name):
            if id(obj) in visited:
                return False
            visited.add(id(obj))
            for e in obj.extends:
                if name == e.name or _does_extend(e, name):
                    return True
            return False
        return _does_extend(self, name)


classes = list(map(
    lambda x: x[1],
    inspect.getmembers(sys.modules[__name__],
                       lambda c: inspect.isclass(c)
                       and issubclass(c, ModelElement)
                       and not c.__name__.endswith('Inst')
                       and c.__name__ not in ['ModelElement']))) + common_classes
