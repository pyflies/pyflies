import sys
import inspect
import random
from operator import or_, and_, not_, eq, ne, lt, gt, le, ge, add, sub, mul, truediv, neg
from functools import reduce
from itertools import cycle, repeat, product

from .exceptions import PyFliesException
from .time import TimeReferenceInst
from .stimuli import StimulusSpecInst, StimulusInst, StimulusParamInst
from .scope import ScopeProvider, Postpone, PostponedEval


def get_parent_of_type(clazz, obj):
    if isinstance(obj, clazz):
        return obj
    if hasattr(obj, 'parent'):
        return get_parent_of_type(clazz, obj.parent)


class ModelElement:
    def __init__(self, *args, **kwargs):
        if args:
            self.parent = args[0]
        for k, i in kwargs.items():
            setattr(self, k, i)
        super().__init__()

    def get_scope(self):
        return get_parent_of_type(ScopeProvider, self)

    def get_context(self, local_context=None):
        """
        Return the full context by recursively following scopes up the
        containment hierarchy.
        """
        if local_context is None:
            local_context = {}
        scope = self.get_scope()
        if scope is None:
            return local_context
        c = dict(scope.var_vals)
        c.update(local_context)

        # Follow parent scope hierarchy
        p = scope
        while hasattr(p, 'parent') and p.parent is not None:
            p = p.parent
            if hasattr(p, 'get_context'):
                return p.get_context(c)

        return c


class PyFliesModel(ScopeProvider, ModelElement):
    pass


class VariableAssignment(ModelElement):
    def __repr__(self):
        return '{} = {}'.format(self.name, self.value)


class ExpressionElement(ModelElement):
    def reduce(self):
        """
        Return reduced version of the expression if possible
        """
        return self

    def resolve(self, context=None):
        """
        If this expression element is resolvable (e.g. VariableRef), try to
        resolve in the current context.  This is a default implementation that
        return self.  All resolvable elements should override.
        """
        return self

    def get_operations(self):
        """
        Return iterable of operations
        """
        if hasattr(self, 'opn') and not self.opn:
            # if operation is not given, return identity op
            return cycle([lambda x: x])
        elif type(self.operation) is dict:
            # If multiple operations use a dict to map
            return map(lambda x: self.operation[x], self.opn)
        else:
            # if a single operation, cycle
            return cycle([self.operation])


class Symbol(ExpressionElement):
    def eval(self, context=None):
        return self

    def __eq__(self, other):
        return type(other) is Symbol and self.name == other.name

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Symbol({})'.format(self.name)


class BaseValue(ExpressionElement):
    def eval(self, context=None):
        return self.value

    def __str__(self):
        return str(self.value)


class String(ExpressionElement):
    def eval(self, context=None):
        context = self.get_context(context)
        try:
            return self.value.format(**context)
        except KeyError as k:
            raise PyFliesException('Undefined variable "{}"'.format(k.args[0]))
        except AttributeError:
            if '{' in self.value.replace('{{', ''):
                raise PyFliesException('Undefined variables in "{}"'.format(self.value))
            return self.value

    def __str__(self):
        return self.value


class Sequence(ExpressionElement):
    """
    A sequence of expressions.
    """


class List(Sequence):
    def reduce(self):
        return List(self.parent, values=[x.reduce() for x in self.values])

    def eval(self, context=None):
        res = []
        for v in self.values:
            try:
                res.append(v.eval(context))
            except AttributeError:
                res.append(v)
        return res

    def get_exps(self):
        return self.values

    def __getitem__(self, idx):
        return self.values[idx]

    def __str__(self):
        return '[{}]'.format(', '.join([str(x) for x in self.values]))


class Range(Sequence):
    def eval(self, context=None):
        return list(range(self.lower, self.upper + 1))

    def get_exps(self):
        return [BaseValue(self, value=x) for x in self.eval()]

    def __str__(self):
        return '{}..{}'.format(self.lower, self.upper)


class LoopExpression(ExpressionElement):
    def __str__(self):
        return '{} loop'.format(str(self.exp))

    def reduce(self):
        self.exp = self.exp.reduce()
        return super().reduce()


class MessageExpression(ExpressionElement):
    def eval(self, context=None):
        value = self.value.eval(context)
        if self.message == 'shuffle':
            random.shuffle(value)
            return value
        else:
            return random.choice(value)

    def __str__(self):
        return '{} {}'.format(str(self.value), self.message)


class BinaryOperation(ExpressionElement):
    def reduce(self):
        for idx, op in enumerate(self.op):
            self.op[idx] = op.reduce()
        if len(self.op) == 1:
            return self.op[0]
        else:
            return super().reduce()

    def eval(self, context=None):
        operations = self.get_operations()
        def op(a, b):
            nextop = next(operations)
            try:
                return nextop(a, b)
            except TypeError:
                if type(a) is Symbol:
                    sym = a
                elif type(b) is Symbol:
                    sym = b
                else:
                    raise
                raise PyFliesException('Undefined variable "{}"'.format(sym.name))

        return reduce(op,
                      map(lambda x: x.eval(context) if isinstance(x, ExpressionElement) else x,
                          self.op))

    def __str__(self):
        if len(self.op) > 1:
            a = [str(self.op[0])]
            if hasattr(self, 'opn'):
                opn = self.opn
            else:
                opn = [self.operation_str] * (len(self.op) - 1)
            for oper, op in zip(opn, [str(x) for x in self.op[1:]]):
                a.append(oper)
                a.append(op)
            return ' '.join(a)
        else:
            return str(self.op[0])


class UnaryOperation(ExpressionElement):
    def reduce(self):
        self.op = self.op.reduce()
        if not self.opn:
            return self.op
        else:
            return super().reduce()

    def eval(self, context=None):
        operations = self.get_operations()
        def op(a):
            nextop = next(operations)
            try:
                return nextop(a)
            except TypeError:
                if type(a) is Symbol:
                    raise PyFliesException('Undefined variable "{}"'.format(a.name))
                raise
        inner = self.op.eval(context) if isinstance(self.op, ExpressionElement) else self.op
        return op(inner) if op else inner

    def __str__(self):
        if not self.opn:
            opn = ''
        elif hasattr(self, 'operation_str'):
            opn = self.operation_str + ' '
        else:
            opn = self.opn + ' '
        return '{}{}'.format(opn, str(self.op))


class VariableRef(ExpressionElement):
    def eval(self, context=None):
        context = self.get_context(context)
        try:
            value = context[self.name]
            if type(value) is PostponedEval:
                raise Postpone('Postponed evaluation of "{}"'.format(self.name))
            return value

        except KeyError:
            # If variable is not defined consider it a symbol
            return Symbol(self.parent, name=self.name)

    def resolve(self):
        resolved = self.get_scope().get(self.name)
        if resolved is not None:
            return resolved
        return self

    def __str__(self):
        return self.name


class IfExpression(ExpressionElement):
    def eval(self, context=None):

        cond = self.cond.eval(context)
        if cond is True:
            return self.if_true.eval(context)
        else:
            return self.if_false.eval(context)

    def __str__(self):
        return '{} if {} else {}'.format(self.if_true, self.cond, self.if_false)


class OrExpression(BinaryOperation):
    operation = or_
    operation_str = 'or'


class AndExpression(BinaryOperation):
    operation = and_
    operation_str = 'and'


class NotExpression(UnaryOperation):
    operation = not_
    operation_str = 'not'


class ComparisonExpression(BinaryOperation):
    operation = {
        '==': eq,
        '!=': ne,
        '<=': le,
        '>=': ge,
        '<': lt,
        '>': gt
    }

class AdditiveExpression(BinaryOperation):
    operation = {
        '+': add,
        '-': sub
    }

class MultiplicativeExpression(BinaryOperation):
    operation = {
        '*': mul,
        '/': truediv
    }

class UnaryExpression(UnaryOperation):
    operation = {
        '-': neg,
        '+': lambda x: x
    }

class Condition(ModelElement):
    def __getitem__(self, idx):
        return self.var_exps[idx]

    def __iter__(self):
        return iter(self.var_exps)

    def __len__(self):
        return len(self.var_exps)


class TimeReference(ModelElement):
    def eval(self, context=None):
        return TimeReferenceInst(self, context)


class StimulusSpec(ModelElement):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        if self.at is None:
            # Default time reference
            self.at = TimeReference(self, start_relative=True, relative_op='+',
                                    time=None)
            self.at.time = BaseValue(parent=self.at, value=0)

        if self.duration is None:
            # Default duration is 0, meaning indefinite
            self.duration = BaseValue(parent=self, value=0)

    def eval(self, context=None, last_stim=None):
        return StimulusSpecInst(self, context, last_stim)


class Stimulus(ModelElement):
    def eval(self, context=None):
        return StimulusInst(self, context)


class StimulusParam(ModelElement):
    def eval(self, context=None):
        return StimulusParamInst(self, context)


class ConditionsTable(ModelElement):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        from .table import get_column_widths
        self.column_widths = get_column_widths(self.variables, self.cond_specs)

    def expand(self):
        """
        Expands the table taking into account `loop` messages for looping, and
        ranges and list for cycling.
        """

        from .table import ExpTable, ExpTableRow

        self.expanded = ExpTable(self)

        for cond_spec in self:
            cond_template = []
            loops = []
            loops_idx = []

            # Create cond template which will be used to instantiate concrete
            # expanded table rows.
            for idx, var_exp in enumerate(cond_spec):
                if type(var_exp) is LoopExpression:
                    loops.append(var_exp.exp.resolve())
                    loops_idx.append(idx)
                    cond_template.append(None)
                else:
                    # If not a loop expression then cycle if list-like
                    # expression (e.g. List or Range) or repeat otherwise
                    var_exp_resolved = var_exp.resolve()
                    if isinstance(var_exp_resolved, Sequence):
                        cond_template.append(cycle(var_exp_resolved.get_exps()))
                    else:
                        cond_template.append(repeat(var_exp))

            assert len(cond_template) == len(cond_spec)

            # Evaluate template making possibly new rows if there are loop
            # expressions
            if loops:
                loops = product(*loops)
                for loop_vals in loops:

                    # Evaluate looping variables. We start with all variables
                    # in postponed state to enable postponing evaluation of all
                    # expressions that uses postponed table variables (i.e.
                    # referencing forward column value)
                    row = [None] * len(cond_template)
                    for idx, loop_val in zip(loops_idx, loop_vals):
                        row[idx] = loop_val

                    for idx, cond_i in enumerate(cond_template):
                        if cond_i is not None:
                            row[idx] = next(cond_i)

                    row = ExpTableRow(self.expanded, row)
                    row.eval()
            else:
                # No looping - just evaluate all expressions
                row = ExpTableRow(self.expanded, [next(x) for x in cond_template])
                row.eval()

        self.expanded.calculate_column_widths()

    def calc_phases(self):
        self.expanded.calc_phases()

    def __getitem__(self, idx):
        return self.cond_specs[idx]

    def __iter__(self):
        return iter(self.cond_specs)

    def __len__(self):
        return len(self.cond_specs)

    def __eq__(self, other):
        return self.expanded == other.expanded

    def __str__(self):
        """
        String representation will be in orgmode table format for better readability.
        """
        return self.to_str()

    def to_str(self, expanded=True):
        if expanded:
            return str(self.expanded)
        else:
            from .table import table_to_str
            rows = [spec.var_exps for spec in self.cond_specs]
            return table_to_str(self.variables, rows, self.column_widths)

    def connect_stimuli(self, stimuli):
        """
        For each table condition, and each phase, evaluates stimuli and connect
        matched stimuli to the table/condition phase.  Table must be previously
        expanded.
        """
        if not self.is_expanded():
            raise PyFliesException('Cannot evaluate stimuli on unexpanded table.')


class TestType(CustomClass):
    def calc_phases(self):
        self.table.calc_phases()


custom_classes = list(map(
    lambda x: x[1],
    inspect.getmembers(sys.modules[__name__],
                       lambda c: inspect.isclass(c)
                       and issubclass(c, ModelElement)
                       and c.__name__ not in ['ModelElement',
                                              'ExpressionElement',
                                              'Sequence',
                                              'Symbol',
                                              'BinaryOperation',
                                              'UnaryOperation'])))
