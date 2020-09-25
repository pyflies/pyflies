import sys
import inspect
import random
from operator import or_, and_, not_, eq, ne, lt, gt, le, ge, add, sub, mul, truediv, neg
from functools import reduce
from itertools import cycle, repeat, product
from textx import get_model

from .exceptions import PyFliesException
from .table import ExpTable, get_column_widths, table_to_str, row_to_str
from .time import TimeReferenceInst
from .stimuli import StimulusSpecInst, StimulusInst, StimulusParamInst


class Postpone(BaseException):
    """
    Used to indicate that evaluation cannot be done at this time.
    E.g., in case of forward references during table row evaluation.
    """
    pass


class PostponedEval:
    def __init__(self, exp):
        self.exp = exp

    def __str__(self):
        return 'PostponedEval({})'.format(str(self.exp))

    def __repr__(self):
        return str(self)


class CustomClass:
    def __init__(self, parent, **kwargs):
        self.parent = parent
        for k, i in kwargs.items():
            setattr(self, k, i)


class VariableAssignment(CustomClass):
    def __init__(self, parent, name, value):
        # Keep variable values on the model
        # for use in expressions
        model = get_model(self)
        if not hasattr(model, 'var_vals'):
            model.var_vals = {}
        model.var_vals[name] = value.eval() if isinstance(value, ExpressionElement) else value

    def __repr__(self):
        return '{} = {}'.format(self.name, self.value)


class ExpressionElement(CustomClass):
    def reduce(self):
        """
        Return reduced version of the expression if possible
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

    def get_context(self, local_context):
        model = get_model(self)
        try:
            c = dict(model.var_vals)
        except AttributeError:
            c = {}
        if local_context:
            c.update(local_context)
        return c


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


class List(ExpressionElement):
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

    def __getitem__(self, idx):
        return self.values[idx]

    def __str__(self):
        return '[{}]'.format(', '.join([str(x.reduce()) for x in self.values]))


class Range(ExpressionElement):
    def eval(self, context=None):
        return list(range(self.lower, self.upper + 1))

    def __str__(self):
        return '{}..{}'.format(self.lower, self.upper)


class LoopExpression(ExpressionElement):
    def __str__(self):
        return '{} loop'.format(str(self.exp))


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
        if len(self.op) == 1:
            return self.op[0].reduce()
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
            a = [str(self.op[0].reduce())]
            if hasattr(self, 'opn'):
                opn = self.opn
            else:
                opn = [self.operation_str] * (len(self.op) - 1)
            for oper, op in zip(opn, [str(x.reduce()) for x in self.op[1:]]):
                a.append(oper)
                a.append(op)
            return ' '.join(a)
        else:
            return str(self.op[0])


class UnaryOperation(ExpressionElement):
    def reduce(self):
        if not self.opn and isinstance(self.op, ExpressionElement):
            return self.op.reduce()
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
            if type(value) is Postpone:
                raise Postpone('Postponed evaluation of "{}"'.format(self.name))
            return value

        except KeyError:
            # If variable is not defined consider it a symbol
            return Symbol(self.parent, name=self.name)

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
        return '{} if {} else {}'.format(self.if_true.reduce(),
                                         self.cond.reduce(),
                                         self.if_false.reduce())


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

class Condition(CustomClass):
    def __init__(self, *args, **kwargs):
        # Reduce all condition expressions
        for idx, var_exp in enumerate(self.var_exps):
            self.var_exps[idx] = var_exp.reduce()

    def __getitem__(self, idx):
        return self.var_exps[idx]

    def __iter__(self):
        return iter(self.var_exps)

    def __len__(self):
        return len(self.var_exps)


class TimeReference(ExpressionElement):
    def eval(self, context=None):
        return TimeReferenceInst(self, context)


class StimulusSpec(ExpressionElement):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        if self.at is None:
            # Default time reference
            self.at = TimeReference(self, start_relative=True, relative_op='+',
                                    time=AdditiveExpression(self, op=[0], opn=None))
        if self.duration is None:
            # Default duration is 0, meaning indefinite
            self.duration = AdditiveExpression(self, op=[0], opn=None)

    def eval(self, context=None):
        return StimulusSpecInst(self, context)


class Stimulus(ExpressionElement):
    def eval(self, context=None):
        return StimulusInst(self, context)


class StimulusParam(ExpressionElement):
    def eval(self, context=None):
        return StimulusParamInst(self, context)


class ConditionsTable(CustomClass):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.column_widths = get_column_widths(self.variables, self.condition_specs)

    def expand(self):
        """
        Expands the table taking into account `loop` messages for looping, and
        ranges and list for cycling.
        """

        self.exp_table = ExpTable(self)

        for c in self:
            cond_template = []
            loops = []
            loops_idx = []

            # Create cond template which will be used to instantiate concrete
            # expanded table rows.
            for idx, var_exp in enumerate(c):
                var_exp = var_exp.reduce()
                if type(var_exp) is LoopExpression:
                    loops.append(var_exp.exp.eval())
                    loops_idx.append(idx)
                    cond_template.append(None)
                else:
                    if type(var_exp) in [List, Range] \
                       or (type(var_exp) is VariableRef
                           and type(var_exp.eval()) is list):
                        cond_template.append(cycle(var_exp.eval()))
                    else:
                        cond_template.append(repeat(var_exp))

            assert len(cond_template) == len(c)
            # Evaluate template making possibly new rows if there are loop
            # expressions
            if loops:
                loops = product(*loops)
                for loop_vals in loops:

                    # Evaluate looping variables. We start with all variables
                    # in postponed state to enable postponing evaluation of all
                    # expressions that uses postponed table variables (i.e.
                    # referencing forward column value)
                    context = dict([(v, Postpone()) for v in self.variables])
                    row = self.exp_table.new_row([None] * len(cond_template))
                    for loop_val, idx in zip(loop_vals, loops_idx):
                        row[idx] = loop_val
                        context[self.variables[idx]] = loop_val

                    for idx, cond_i in enumerate(cond_template):
                        if cond_i is not None:
                            row[idx] = PostponedEval(next(cond_i))

                    row.eval(context)
            else:
                # No looping - just evaluate all expressions
                context = dict([(v, Postpone()) for v in self.variables])
                row = self.exp_table.new_row([PostponedEval(next(x)) for x in cond_template])
                row.eval(context)

        self.exp_table.calculate_column_widths()

    def __getitem__(self, idx):
        return self.condition_specs[idx]

    def __iter__(self):
        return iter(self.condition_specs)

    def __len__(self):
        return len(self.condition_specs)

    def __eq__(self, other):
        return self.exp_table == other.exp_table

    def __str__(self):
        """
        String representation will be in orgmode table format for better readability.
        """
        return self.to_str()

    def to_str(self, expanded=True):
        rows = [spec.var_exps for spec in self.condition_specs]
        if expanded:
            return table_to_str(self.variables, self.exp_table,
                                self.exp_table.column_widths)
        else:
            return table_to_str(self.variables, rows, self.column_widths)

    def connect_stimuli(self, stimuli):
        """
        For each table condition, and each phase, evaluates stimuli and connect
        matched stimuli to the table/condition phase.  Table must be previously
        expanded.
        """
        if not self.is_expanded():
            raise PyFliesException('Cannot evaluate stimuli on unexpanded table.')


custom_classes = list(map(
    lambda x: x[1],
    inspect.getmembers(sys.modules[__name__],
                       lambda c: inspect.isclass(c)
                       and issubclass(c, CustomClass)
                       and c.__name__ not in ['CustomClass',
                                              'ExpressionElement',
                                              'BinaryOperation',
                                              'UnaryOperation'])))
