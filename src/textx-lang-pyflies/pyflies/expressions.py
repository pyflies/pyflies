import sys
import inspect
import random
from operator import or_, and_, not_, eq, ne, lt, gt, le, ge, add, sub, mul, truediv, neg
from functools import reduce
from itertools import cycle
from textx import get_model

from pyflies.exceptions import PyFliesException


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


class String(ExpressionElement):
    def eval(self):
        model = get_model(self)
        try:
            return self.val.format(**model.var_vals)
        except KeyError as k:
            raise PyFliesException('Undefined variable "{}"'.format(k.args[0]))
        except AttributeError:
            if '{' in self.val.replace('{{', ''):
                raise PyFliesException('Undefined variables in "{}"'.format(self.val))
            return self.val


class List(ExpressionElement):
    def eval(self):
        res = []
        for v in self.values:
            try:
                res.append(v.eval())
            except AttributeError:
                res.append(v)
        return res


class Range(ExpressionElement):
    def eval(self):
        return list(range(self.lower, self.upper + 1))


class MessageExpression(ExpressionElement):
    def eval(self):
        value = self.value.eval()
        if self.message == 'shuffle':
            random.shuffle(value)
            return value
        else:
            return random.choice(value)


class BinaryOperation(ExpressionElement):
    def eval(self):
        operations = self.get_operations()
        def op(a, b):
            nextop = next(operations)
            return nextop(a, b)
        return reduce(op,
                      map(lambda x: x.eval() if isinstance(x, ExpressionElement) else x,
                          self.op))


class UnaryOperation(ExpressionElement):
    def eval(self):
        operations = self.get_operations()
        def op(a):
            nextop = next(operations)
            return nextop(a)
        inner = self.op.eval() if isinstance(self.op, ExpressionElement) else self.op
        return op(inner) if op else inner


class VariableRef(ExpressionElement):
    def eval(self):
        model = get_model(self)
        try:
            return model.var_vals[self.name]
        except (KeyError, AttributeError):
            raise PyFliesException('Undefined variable "{}"'.format(self.name))


class Expression(BinaryOperation):
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


custom_exp_classes = list(map(
    lambda x: x[1],
    inspect.getmembers(sys.modules[__name__],
                       lambda c: inspect.isclass(c)
                       and issubclass(c, CustomClass)
                       and c.__name__ not in ['CustomClass',
                                              'ExpressionElement',
                                              'BinaryOperation',
                                              'UnaryOperation'])))
