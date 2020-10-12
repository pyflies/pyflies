"""
Custom classes for pyflies.tx
"""
import sys
import inspect
import random
from operator import or_, and_, not_, eq, ne, lt, gt, le, ge, add, sub, mul, truediv, neg
from functools import reduce
from itertools import cycle, repeat, product

from pyflies.exceptions import PyFliesException
from pyflies.time import TimeReferenceInst
from pyflies.components import ComponentTimeInst, ComponentInst, ComponentParamInst
from pyflies.scope import ScopeProvider, Postpone, PostponedEval

from .common import ModelElement, classes as common_classes, BaseValue, LoopExpression, Sequence


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

    def expand(self):
        """
        Expands the table taking into account `loop` messages for looping, and
        ranges and list for cycling.
        """

        from pyflies.table import ExpTable, ExpTableRow

        table = ExpTable(self)
        self.parent.table = table

        for cond_spec in self:
            cond_template = []
            loops = []
            loops_idx = []

            # First check to see if there is loops and if sequences
            # This will influence the interpretation of the row
            has_loops = any([type(v) is LoopExpression for v in cond_spec])
            has_sequences = any([isinstance(v.resolve(), Sequence) for v in cond_spec])
            should_repeat = has_loops or has_sequences
            if not has_loops and has_sequences:
                # There are sequences but no loops. We shall do iteration for
                # the length of the longest sequence. Other sequences will
                # cycle. Base values will repeat.
                max_len = max([len(x.resolve())
                               for x in cond_spec if isinstance(x.resolve(), Sequence)])

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
                        if has_loops or len(var_exp_resolved) < max_len:
                            cond_template.append(cycle(var_exp_resolved))
                        else:
                            cond_template.append(iter(var_exp_resolved))
                    else:
                        if has_sequences:
                            cond_template.append(repeat(var_exp))
                        else:
                            cond_template.append(iter([var_exp]))

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

                    row = ExpTableRow(table, row)
                    row.eval()
            else:
                # No looping - just evaluate all expressions until all
                # iterators are exhausted
                try:
                    while True:
                        row = ExpTableRow(table, [next(x) for x in cond_template])
                        row.eval()
                except StopIteration:
                    pass

        table.calculate_column_widths()

    def calc_phases(self):
        self.parent.table.calc_phases()

    def __getitem__(self, idx):
        return self.cond_specs[idx]

    def __iter__(self):
        return iter(self.cond_specs)

    def __len__(self):
        return len(self.cond_specs)

    def __eq__(self, other):
        return self.parent.table == other.parent.table

    def __str__(self):
        """
        String representation will be in orgmode table format for better readability.
        """
        return self.to_str()

    def to_str(self, expanded=True):
        if expanded:
            return str(self.parent.table)
        else:
            from pyflies.table import table_to_str
            rows = [spec.var_exps for spec in self.cond_specs]
            return table_to_str(self.variables, rows, self.column_widths)

    def connect_components(self, components):
        """
        For each table condition, and each phase, evaluates components and connect
        matched components to the table/condition phase.  Table must be previously
        expanded.
        """
        if not self.is_expanded():
            raise PyFliesException('Cannot evaluate components on unexpanded table.')


class Test(ModelElement, ScopeProvider):
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
        self.components = components

    def calc_phases(self):
        self.table.calc_phases()

    def __repr__(self):
        return '<Test:{}>'.format(self.name)


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
                                              'UnaryOperation']))) + common_classes
