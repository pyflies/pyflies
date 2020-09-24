import sys
import inspect
import random
from operator import or_, and_, not_, eq, ne, lt, gt, le, ge, add, sub, mul, truediv, neg
from functools import reduce
from itertools import cycle, repeat, product
from textx import get_model

from pyflies.exceptions import PyFliesException


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


class TimeReference(CustomClass):
    pass


class StimulusSpec(CustomClass):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        if self.at is None:
            # Default time reference
            self.at = TimeReference(self, start_relative=True, relative_op='+', time=0)


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
        model = get_model(self)
        try:
            return self.value.format(**model.var_vals)
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
        model = get_model(self)
        try:
            c = dict(model.var_vals)
        except AttributeError:
            c = {}
        try:
            if context:
                c.update(context)

            value = c[self.name]
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

class ConditionsTable(CustomClass):
    def is_expanded(self):
        return hasattr(self, 'conditions')

    def expand(self):
        """
        Expands the table taking into account `loop` messages for looping, and
        ranges and list for cycling.
        """

        def evaluate_condition(condition):
            """
            All condition variable values must be evaluated to base
            values or symbols. Do this in loop because there can be
            forward references. If we pass a full loop and no value
            has been resolved we have cyclic reference
            """
            while True:
                all_resolved = all([not type(c) is PostponedEval for c in condition])
                if all_resolved:
                    break
                resolved = False
                for idx, c in enumerate(condition):
                    if type(c) is PostponedEval:
                        try:
                            cond_value = c.exp.eval(row_context)
                            condition[idx] = cond_value
                            if type(cond_value) in [BaseValue, Symbol]:
                                row_context[self.variables[idx]] = cond_value
                            resolved = True
                        except Postpone:
                            pass
                if not resolved:
                    raise PyFliesException(
                        'Cyclic dependency in table. Row {}.'.format(condition))

        self.conditions = []

        for c in self.condition_specs:
            cond_template = []
            loops = []
            loops_idx = []
            # Create cond template
            for idx, var_exp in enumerate(c.var_exps):
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

            assert len(cond_template) == len(c.var_exps)
            # Evaluate template making possibly new rows if there are loop
            # expressions
            if loops:
                loops = product(*loops)
                for loop_vals in loops:

                    # Evaluate looping variables
                    row_context = dict([(v, Postpone()) for v in self.variables])
                    condition = [None] * len(cond_template)
                    for loop_val, idx in zip(loop_vals, loops_idx):
                        condition[idx] = loop_val
                        row_context[self.variables[idx]] = loop_val

                    for idx, cond_i in enumerate(cond_template):
                        if cond_i is not None:
                            condition[idx] = PostponedEval(next(cond_i))

                    evaluate_condition(condition)

                    self.conditions.append(condition)
            else:
                # No looping - just evaluate all expressions
                row_context = dict([(v, Postpone()) for v in self.variables])
                condition = [PostponedEval(next(x)) for x in cond_template]
                evaluate_condition(condition)
                self.conditions.append(condition)

    def __str__(self):
        """
        String representation will be in orgmode table format for better readability.
        Also, by default, expanded version will be used if exists.
        """
        if self.is_expanded():
            return self.to_str()
        else:
            self.to_str([spec.var_exps for spec in self.condition_specs])

    def to_str(self, expanded=True):

        if expanded and not self.is_expanded():
            raise PyFliesException('Table is not expanded. Expand it first or use `expanded=False`.')

        if self.is_expanded():
            table = self.conditions
        else:
            table = [list(spec.var_exps) for spec in self.condition_specs]

        column_widths = [len(x) + 2 for x in self.variables]
        for row in table:
            for idx, element in enumerate(row):
                str_rep = str(element)
                row[idx] = str_rep
                if column_widths[idx] < len(str_rep) + 2:
                    column_widths[idx] = len(str_rep) + 2

        def get_row(row):
            str_row = '|'
            for idx, element in enumerate(row):
                str_row += ' ' + element.ljust(column_widths[idx] - 1) + '|'
            return str_row

        str_rep = get_row(self.variables)
        str_rep += '\n|' + '+'.join(['-' * x for x in column_widths]) + '|\n'
        str_rep += '\n'.join([get_row(row) for row in table])

        return str_rep

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
