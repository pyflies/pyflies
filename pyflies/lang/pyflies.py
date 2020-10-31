"""
Custom classes for pyflies.tx
"""
import sys
import inspect
import random
import jinja2

from pyflies.exceptions import PyFliesException
from pyflies.time import TimeReferenceInst
from pyflies.components import ComponentTimeInst, ComponentInst, ComponentParamInst
from pyflies.scope import ScopeProvider
from pyflies.evaluated import EvaluatedBase
from pyflies.table import ConditionsTableInst

from .common import ModelElement, classes as common_classes, BaseValue


def get_parent_of_type(clazz, obj):
    if isinstance(obj, clazz):
        return obj
    if hasattr(obj, 'parent'):
        return get_parent_of_type(clazz, obj.parent)


class PyFliesModel(ScopeProvider, ModelElement):
    pass


class VariableAssignment(ModelElement):
    def __repr__(self):
        return '{} = {}'.format(self.name, self.value)


class Condition(ModelElement):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        # Unpack table expressions
        self.var_exps = [te.exp for te in self.var_exps]

    def __getitem__(self, idx):
        return self.var_exps[idx]

    def __iter__(self):
        return iter(self.var_exps)

    def __len__(self):
        return len(self.var_exps)


class TimeReference(ModelElement):
    def eval(self, context=None):
        return TimeReferenceInst(self, context)


class ComponentTime(ModelElement):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        if self.at is None:
            # Default time reference
            self.at = TimeReference(self, start_relative=True, relative_op='+',
                                    relative_to=None, time=None)
            self.at.time = BaseValue(parent=self.at, value=0)

        if self.duration is None:
            # Default duration is 0, meaning indefinite
            self.duration = BaseValue(parent=self, value=0)

    def eval(self, context=None, last_stim=None):
        return ComponentTimeInst(self, context, last_stim)


class Component(ModelElement):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # Create default parameters specs following inheritance chain
        # of component types
        comp_type = self.type
        all_params = list(self.params)

        def get_inherited(comp_type):
            for param_type in comp_type.param_types:
                if param_type.name not in [x.type.name for x in all_params]:
                    all_params.append(ComponentParam(parent=self,
                                                     type=param_type,
                                                     value=param_type.default))
            for inh_comp in comp_type.extends:
                get_inherited(inh_comp)
        get_inherited(comp_type)
        self.all_params = all_params

    def eval(self, context=None):
        return ComponentInst(self, context)


class ComponentParam(ModelElement):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # TODO. Check component param type

    def eval(self, context=None):
        return ComponentParamInst(self, context)


class ConditionsTable(ModelElement):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        from pyflies.table import get_column_widths
        self.column_widths = get_column_widths(self.variables, self.cond_specs)

    def eval(self, context=None):
        """
        Expands the table taking into account `loop` messages for looping, and
        ranges and lists for cycling.
        """
        return ConditionsTableInst(self, context)

    def __getitem__(self, idx):
        return self.cond_specs[idx]

    def __iter__(self):
        return iter(self.cond_specs)

    def __len__(self):
        return len(self.cond_specs)

    def __str__(self):
        """
        String representation will be in orgmode table format for better readability.
        """
        return self.to_str()

    def to_str(self):
        from pyflies.table import table_to_str
        rows = [spec.var_exps for spec in self.cond_specs]
        return table_to_str(self.variables, rows, self.column_widths)


class TestType(ModelElement, ScopeProvider):

    def instantiate_default_components(self):
        """
        Create component instances with default values.
        Used for targets that needs upfront component initialization.
        """
        components = []
        for ccond in self.components_cond:
            for ctimes in ccond.comp_times:
                comp_spec = ctimes.component
                component = ComponentInst(comp_spec)
                components.append(component)

                # Add named components to this scope to be referencable from
                # expressions
                if component.spec.parent.name:
                    assgn = VariableAssignment(self, name=component.spec.parent.name,
                                               value=None)
                    assgn.value = BaseValue(parent=assgn, value=component)
                    self.vars.append(assgn)

                    # Check if we have name clash
                    comp_name = component.spec.parent.name
                    if comp_name in self.var_vals \
                       or comp_name in self.table_spec.variables:
                        raise PyFliesException(
                            'Cannot name component "{}" as that '
                            'variable already exists in the scope'.format(comp_name))
                    self.var_vals[comp_name] = component

        self.components = components

    def __repr__(self):
        return '<TestType:{}>'.format(self.name)


class Block(ModelElement):
    def eval(self, context):
        insts = []
        statements = self.statements
        if self.random:
            random.sample(statements, len(statements))

        for s in statements:
            insts.extend(s.eval(context))

        return insts


class Repeat(ModelElement):
    def eval(self, context):
        insts = []
        if self._with:
            table = self._with.eval(context)
            cond_var_names = self._with.variables
            for row in table:
                context = dict(context)
                context.update(zip(cond_var_names, row))
                insts.extend(self.what.eval(context))
        else:
            if self.times is None:
                times = 1
            else:
                times = self.times.eval(context)
            for idx in range(times):
                context = dict(context)
                if times > 1 or 'repeat_index' not in context:
                    context['repeat_index'] = idx + 1
                insts.extend(self.what.eval(context))

        return insts


class Show(ModelElement):
    def eval(self, context):
        return self.screen.eval(context, duration=self.duration)


class Test(ModelElement):
    def eval(self, context):
        context = dict(context)
        context.update({'practice': False})
        context.update({a.name: a.value.eval(context) for a in self.args})
        return [TestInst(self.type, context)]


class TestInst(EvaluatedBase):
    def __init__(self, spec, context):
        super().__init__(spec)
        self.practice = context.get('practice', False)
        self.random = context.get('random', False)
        self.table = spec.table_spec.eval(context)
        self.table.calc_phases(context)


class Screen(ModelElement):
    def eval(self, context=None, duration=0):
        context = dict(context)
        context.update({a.name: a.value.eval(context) for a in self.args})
        return [ScreenInst(self.type, duration, context)]


class ScreenInst(EvaluatedBase):
    def __init__(self, spec, duration, context):
        super().__init__(spec)
        self.content = jinja2.Template(spec.content).render(**context)
        self.duration = duration.eval() if duration is not None else 0


class Flow(ModelElement):
    def eval(self, context=None):
        context = self.get_context(context)
        self.insts = self.block.eval(context)


classes = list(map(
    lambda x: x[1],
    inspect.getmembers(sys.modules[__name__],
                       lambda c: inspect.isclass(c)
                       and issubclass(c, ModelElement)
                       and not c.__name__.endswith('Inst')
                       and c.__name__ not in ['ModelElement',
                                              'ExpressionElement',
                                              'Sequence',
                                              'Symbol',
                                              'BinaryOperation',
                                              'UnaryOperation']))) + common_classes
