"""
Custom classes for common.tx
"""
import sys
import inspect
import random
import jinja2
from operator import or_, and_, not_, eq, ne, lt, gt, le, ge, add, sub, mul, truediv, neg
from functools import reduce
from itertools import cycle
from textx import get_children_of_type
from textx.const import MULT_ONE, MULT_OPTIONAL

from pyflies.exceptions import PyFliesException
from pyflies.scope import ScopeProvider, Postpone, PostponedEval


def get_parent_of_type(clazz, obj):
    if isinstance(obj, clazz):
        return obj
    if hasattr(obj, 'parent'):
        return get_parent_of_type(clazz, obj.parent)


def reduce_exp(obj):
    """
    Descends down the containment tree and reduce all expressions.
    """

    visited = set()

    def inner_reduce_exp(obj):

        if id(obj) in visited:
            return
        visited.add(id(obj))

        cls = obj.__class__
        if hasattr(cls, '_tx_attrs'):
            for attr_name, attr in obj._tx_attrs.items():
                if attr.mult in (MULT_ONE, MULT_OPTIONAL):
                    new_elem = getattr(obj, attr_name)
                    if new_elem is not None:
                        if isinstance(new_elem, ExpressionElement):
                            reduced = new_elem.reduce()
                            reduced.parent = obj
                            setattr(obj, attr_name, reduced)
                        else:
                            inner_reduce_exp(new_elem)
                else:
                    new_elem_list = getattr(obj, attr_name)
                    if new_elem_list:
                        for idx, new_elem in enumerate(new_elem_list):
                            if isinstance(new_elem, ExpressionElement):
                                reduced = new_elem.reduce()
                                new_elem_list[idx] = reduced
                            else:
                                inner_reduce_exp(new_elem)

    inner_reduce_exp(obj)


def unresolvable_refs(exp):
    """
    Find all variable refs in the given expression that can't be resolved.
    """
    unresolvable = []
    var_refs = get_children_of_type("VariableRef", exp)
    while var_refs:
        var_ref = var_refs.pop()
        scope = var_ref.get_scope()
        if scope is None:
            continue
        resolved_ref = {v.name: v.value
                        for v in scope.vars}.get(var_ref.name, var_ref)
        if resolved_ref is var_ref:
            unresolvable.append(var_ref)
        else:
            new_var_refs = get_children_of_type("VariableRef", resolved_ref)
            var_refs.extend(new_var_refs)
    return unresolvable


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


class ExpressionElement(ModelElement):
    def reduce(self):
        """
        Return reduced version of the expression if possible
        """
        return self

    def resolve(self, context=None):
        """
        If this expression element is resolvable (e.g. VariableRef), try to
        resolve in the current scope.  This is a default implementation that
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
        return str(self) == str(other)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class BaseValue(ExpressionElement):
    def eval(self, context=None):
        return self.value

    def __str__(self):
        return str(self.value)


class String(ExpressionElement):
    def eval(self, context=None):
        context = self.get_context(context)

        # Check for unexisting variables
        for sp in self.value.split('{{'):
            if '}}' in sp:
                # This is variable. Check if exists.
                var_name = sp.split('}}')[0]
                if var_name not in context:
                    raise PyFliesException('Undefined variable "{}"'.format(var_name))

        return jinja2.Template(self.value).render(**context)

    def __str__(self):
        return self.value


class Sequence(ExpressionElement):
    """
    A sequence of expressions.
    """
    def __getitem__(self, idx):
        return self.values[idx]

    def __iter__(self):
        return iter(self.values)

    def __len__(self):
        return len(self.values)


class List(Sequence):
    def reduce(self):
        self.values = [x.reduce() for x in self.values]
        return super().reduce()

    def eval(self, context=None):
        res = []
        for v in self.values:
            try:
                res.append(v.eval(context))
            except AttributeError:
                res.append(v)
        return res

    def __str__(self):
        return '[{}]'.format(', '.join([str(x) for x in self.values]))


class Range(List):
    def reduce(self):
        self.lower = self.lower if type(self.lower) is int else self.lower.reduce()
        self.upper = self.upper if type(self.upper) is int else self.upper.reduce()
        return self

    def eval(self, context=None):
        lower = self.lower if type(self.lower) is int else self.lower.eval(context)
        upper = self.upper if type(self.upper) is int else self.upper.eval(context)
        return list(range(lower, upper + 1))

    def resolve(self, context):
        return List(self.parent, values=[BaseValue(self, value=x)
                                         for x in self.eval(context)])

    def __str__(self):
        return '{}..{}'.format(self.lower, self.upper)


class Point(ExpressionElement):
    def __str__(self):
        return '({}, {})'.format(self.x, self.y)


class LoopExpression(ExpressionElement):
    def __str__(self):
        return '{} loop'.format(str(self.exp))

    def reduce(self):
        self.exp = self.exp.reduce()
        return super().reduce()


class MessageExpression(ExpressionElement):
    def eval(self, context=None):
        value = self.receiver.eval(context)
        if self.message == 'shuffle':
            random.shuffle(value)
            return value
        else:
            return random.choice(value)

    def __str__(self):
        return '{} {}'.format(str(self.receiver), self.message)


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
                      map(lambda x: x.eval(context)
                          if isinstance(x, ExpressionElement) else x,
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
        inner = self.op.eval(context) \
            if isinstance(self.op, ExpressionElement) else self.op
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

    def resolve(self, context=None):
        """
        Resolve variable in its scope.  If context is provided create BaseValue
        or List for the provided value to enable further proper eval.
        """
        resolved = self.get_scope().get(self.name)
        if resolved is not None:
            if hasattr(resolved, 'resolve'):
                return resolved.resolve(context)
            return resolved
        if context and self.name in context:
            val = context[self.name]
            if type(val) is list:
                return List(self.parent, values=val)
            else:
                return BaseValue(self.parent, value=val)
        return self

    def __repr__(self):
        return self.name


class IfExpression(ExpressionElement):
    def reduce(self):
        self.cond = self.cond.reduce()
        self.if_true = self.if_true.reduce()
        self.if_false = self.if_false.reduce()
        return self

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


classes = list(map(
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
