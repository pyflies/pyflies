from textx import get_children_of_type
from .exceptions import PyFliesException


class Postpone(BaseException):
    """
    Used to indicate that evaluation cannot be done at this time.  E.g., in
    case of forward references during table row evaluation.
    """
    pass


class PostponedEval:
    """
    Actual expression whose evaluation is postponed until referenced variables
    are resolved.
    """
    def __init__(self, exp):
        self.exp = exp

    def __str__(self):
        return 'PostponedEval({})'.format(str(self.exp))

    def __repr__(self):
        return str(self)


class ScopeProvider:
    """
    Scoper providers are containers for variable definitions.  They provide the
    means to evaluate variables, even multiple times, using values from parent
    scope providers (scope providers may nest).  Some scope providers are
    evaluated only once (e.g. PyFliesModel) while others may be evaluated
    multiple times (e.g. condition table rows) to account for the changing
    local context and values which may change on multiple reevaluation (e.g.
    random values).

    This class should be inherited by each model class which represents the
    root of the scope.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.var_vals = {}

        # Collect all variable assignments that belong to this scope.
        # Do not collect child scopes.
        from .lang.pyflies import VariableAssignment
        assignments = get_children_of_type(
            VariableAssignment, self,
            should_follow=lambda obj: not isinstance(obj, ScopeProvider))

        self.vars = assignments

    def get(self, name):
        """
        Search the scope for the given name and return expression if found or
        `None` otherwise.
        """
        for var in self.vars:
            if var.name == name:
                return var.value
        try:
            return self.parent.get_scope().get(name)
        except AttributeError:
            pass

    def eval(self, context=None):
        """
        Evaluates all variables defined in this scope.  Do evaluation in a loop
        with postponing to enable forward referencing.
        """
        self.var_vals = {v.name: PostponedEval(v.value) for v in self.vars}
        context = self.get_context(context)
        while True:
            all_resolved = all((not type(c) is PostponedEval
                                for c in self.var_vals.values()))
            if all_resolved:
                break
            resolved = False
            for name, exp in self.var_vals.items():
                if type(exp) is PostponedEval:
                    try:
                        if hasattr(exp.exp, 'eval'):
                            value = exp.exp.eval(context)
                        else:
                            value = exp.exp
                        context[name] = value
                        self.var_vals[name] = value
                        resolved = True
                    except Postpone:
                        pass

            # If there is not a single resolution in this run we have a cyclic
            # dependency
            if not resolved:
                raise PyFliesException('Cyclic dependency detected.')
