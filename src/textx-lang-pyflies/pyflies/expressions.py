import sys
import inspect
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
        model.var_vals[name] = value

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
