import sys
import inspect
import random
from operator import or_, and_, not_, eq, ne, lt, gt, le, ge, add, sub, mul, truediv, neg
from functools import reduce
from itertools import cycle, repeat, product
from textx import get_model

from pyflies.exceptions import PyFliesException


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
    def __eq__(self, other):
        return type(other) is Symbol and self.name == other.name


class BaseValue(ExpressionElement):
    def eval(self):
        return self.value


class String(ExpressionElement):
    def eval(self):
        model = get_model(self)
        try:
            return self.value.format(**model.var_vals)
        except KeyError as k:
            raise PyFliesException('Undefined variable "{}"'.format(k.args[0]))
        except AttributeError:
            if '{' in self.value.replace('{{', ''):
                raise PyFliesException('Undefined variables in "{}"'.format(self.value))
            return self.value


class List(ExpressionElement):
    def reduce(self):
        return List(self.parent, values=[x.reduce() for x in self.values])

    def eval(self):
        res = []
        for v in self.values:
            try:
                res.append(v.eval())
            except AttributeError:
                res.append(v)
        return res

    def __getitem__(self, idx):
        return self.values[idx]


class Range(ExpressionElement):
    def eval(self):
        return list(range(self.lower, self.upper + 1))


class LoopExpression(ExpressionElement):
    pass


class MessageExpression(ExpressionElement):
    def eval(self):
        value = self.value.eval()
        if self.message == 'shuffle':
            random.shuffle(value)
            return value
        else:
            return random.choice(value)


class BinaryOperation(ExpressionElement):
    def reduce(self):
        if len(self.op) == 1:
            return self.op[0].reduce()
        else:
            return super().reduce()

    def eval(self):
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
                      map(lambda x: x.eval() if isinstance(x, ExpressionElement) else x,
                          self.op))


class UnaryOperation(ExpressionElement):
    def reduce(self):
        if not self.opn and isinstance(self.op, ExpressionElement):
            return self.op.reduce()
        else:
            return super().reduce()

    def eval(self):
        operations = self.get_operations()
        def op(a):
            nextop = next(operations)
            try:
                return nextop(a)
            except TypeError:
                if type(a) is Symbol:
                    raise PyFliesException('Undefined variable "{}"'.format(a.name))
                raise
        inner = self.op.eval() if isinstance(self.op, ExpressionElement) else self.op
        return op(inner) if op else inner


class VariableRef(ExpressionElement):
    def eval(self):
        model = get_model(self)
        try:
            return model.var_vals[self.name]
        except (KeyError, AttributeError):
            # If variable is not defined consider it a symbol
            return Symbol(self.parent, name=self.name)


class IfExpression(ExpressionElement):
    def eval(self):
        cond = self.cond.eval()
        if cond is True:
            return self.if_true.eval()
        else:
            return self.if_false.eval()


class OrExpression(BinaryOperation):
    operation = or_


class AndExpression(BinaryOperation):
    operation = and_


class NotExpression(UnaryOperation):
    operation = not_


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
    def expand(self):
        """
        Expands the table taking into account `loop` messages for looping, and
        ranges and list for cycling.
        """
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
                    condition = [None] * len(cond_template)
                    for loop_val, idx in zip(loop_vals, loops_idx):
                        condition[idx] = loop_val
                    for idx, cond_i in enumerate(cond_template):
                        if cond_i is not None:
                            condition[idx] = next(cond_i)
                    self.conditions.append(condition)
            else:
                # No looping - just evaluate all expressions
                condition = []
                for cond_i in cond_template:
                    condition.append(next(cond_i).eval())
                self.conditions.append(condition)


    def connect_stimuli(self, stimuli):
        """
        For each table condition, and each phase, evaluates stimuli and connect
        matched stimuli to the table/condition phase.  Table must be previously
        expanded.
        """
        if not hasattr(self, 'conditions'):
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
