from itertools import cycle, repeat, product
from .exceptions import PyFliesException
from .scope import ScopeProvider
from .evaluated import EvaluatedBase
from .lang.common import ModelElement, LoopExpression, Symbol


def get_column_widths(variables, rows):
    """
    For the given list of variables and table rows calculate column widths
    based on the longest string representation in each column.
    """
    # Calculate column widths of unexpanded table
    column_widths = [len(x) + 2 for x in variables]
    for row in rows:
        for idx, element in enumerate(row):
            str_rep = str(element)
            if column_widths[idx] < len(str_rep) + 2:
                column_widths[idx] = len(str_rep) + 2
    return column_widths


def header_str(header, column_widths):
    str_rep = row_to_str(header, column_widths)
    str_rep += '\n|' + '+'.join(['-' * x for x in column_widths]) + '|\n'
    return str_rep


def table_to_str(header, rows, column_widths):
    str_rep = header_str(header, column_widths)
    str_rep += '\n'.join([row_to_str(row, column_widths) for row in rows])
    return str_rep


def row_to_str(row, column_widths=None):
    str_row = '|'
    for idx, element in enumerate(row):
        el = str(element)
        if column_widths:
            el = el.ljust(column_widths[idx] - 2)
        str_row += ' ' + el + ' |'
    return str_row


class ConditionsTableInst(EvaluatedBase, ModelElement):
    """
    Represents fully expanded and evaluated Condition table.
    """
    def __init__(self, spec, context):
        super().__init__(spec)
        self.column_widths = None
        self.rows = []
        self.expand(context)

    def expand(self, context):
        for cond_spec in self.spec:
            cond_template = []
            loops = []
            loops_idx = []

            from .lang.common import Sequence
            # First check to see if there is loops and if sequences
            # This will influence the interpretation of the row
            has_loops = any([type(v) is LoopExpression for v in cond_spec])
            resolved_specs = [s.resolve(context) for s in cond_spec]
            sequence_specs = [x for x in resolved_specs if isinstance(x, Sequence)]
            has_sequences = bool(sequence_specs)
            should_repeat = has_loops or has_sequences
            if not has_loops and has_sequences:
                # There are sequences but no loops. We shall do iteration for
                # the length of the longest sequence. Other sequences will
                # cycle. Base values will repeat.
                max_len = max((len(x) for x in sequence_specs))

            # Create cond template which will be used to instantiate concrete
            # expanded table rows.
            for idx, var_exp in enumerate(cond_spec):
                if type(var_exp) is LoopExpression:
                    var_exp_eval = var_exp.exp.eval(context)
                    if type(var_exp_eval) is Symbol:
                        raise PyFliesException('Undefined variable "{}"'
                                               .format(var_exp_eval.name))
                    loops.append(var_exp_eval)
                    loops_idx.append(idx)
                    cond_template.append(None)
                else:
                    # If not a loop expression then cycle if list-like
                    # expression (e.g. List or Range) or repeat otherwise
                    var_exp_resolved = var_exp.resolve(context)
                    if isinstance(var_exp_resolved, Sequence):
                        if has_loops or len(var_exp_resolved) < max_len:
                            cond_template.append(cycle(var_exp_resolved))
                        else:
                            cond_template.append(iter(var_exp_resolved))
                    else:
                        if should_repeat:
                            cond_template.append(repeat(var_exp_resolved))
                        else:
                            cond_template.append(iter([var_exp_resolved]))

            assert len(cond_template) == len(cond_spec)

            # Evaluate template making possibly new rows if there are loop
            # expressions
            if loops:
                # Evaluate all loop expressions
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

                    row = ConditionsTableInstRow(self, row)
                    row.eval(context)
            else:
                # No looping - just evaluate all expressions until all
                # iterators are exhausted
                try:
                    while True:
                        row = ConditionsTableInstRow(
                            self, [next(x) for x in cond_template])
                        row.eval(context)
                except StopIteration:
                    pass

        self.calculate_column_widths()

    def calculate_column_widths(self):
        self.column_widths = get_column_widths(self.spec.variables, self.rows)

    def calc_phases(self, context):
        """
        Evaluates condition components specification from the associated condition
        table for each trial phase.  After evaluation each row will have
        connected appropriate, evaluated components instances.
        """
        for row in self.rows:
            row.calc_phases(context)

    def header_str(self):
        return header_str(self.spec.variables, self.column_widths)

    def __str__(self):
        return table_to_str(self.spec.variables, self.rows, self.column_widths)

    def __getitem__(self, idx):
        return self.rows[idx]

    def __iter__(self):
        return iter(self.rows)

    def __eq__(self, other):
        return self.rows == other.rows


class ConditionsTableInstRow(ModelElement, ScopeProvider):
    def __init__(self, table, exps):
        self.parent = table
        self.exps = exps
        table.rows.append(self)

        # Create variable assignments needed by ScopeProvider.
        # We inherit all standard scope provider mechanics in reference
        # resolving and variable calculation.
        from .lang.pyflies import VariableAssignment
        self.vars = []
        for name, value in zip(self.parent.spec.variables, self.exps):
            self.vars.append(VariableAssignment(self, name=name, value=value))

        # Trial phases
        self.ph_fix = None
        self.ph_exec = None
        self.ph_error = None
        self.ph_correct = None

        # All comp time spec together
        self.comp_times = []

    def calc_phases(self, context):
        """
        Evaluate condition components specification for each phase of this trial.
        If condition is True evaluate components specs and attach to this row.
        """
        phases = ['fix', 'exec', 'error', 'correct']
        for phase in phases:
            row_context = dict(context)
            row_context.update(self.get_context(context))
            row_context.update({phase: True})

            test = self.parent.spec.parent
            # Evaluate test variables in the context of this row
            test.eval(row_context)

            # Update row context with test variables so that they
            # shadow global variables.
            row_context.update(test.get_scope().var_vals)
            # Save context for logging purposes
            self.var_vals.update({k: v for k, v in row_context.items()
                                  if k not in phases})

            for cond_comp in test.components_cond:
                try:
                    cond_val = cond_comp.condition.eval(row_context)
                except PyFliesException:
                    cond_val = False

                if cond_val is True:
                    comp_insts = []
                    last_comp = None
                    for comp_time in cond_comp.comp_times:
                        comp_time_inst = comp_time.eval(row_context, last_comp)
                        comp_insts.append(comp_time_inst)
                        self.comp_times.append(comp_time_inst)
                        last_comp = comp_time
                    setattr(self, f'ph_{phase}', comp_insts)
                    break

    def get_context_noncond(self):
        """
        Returns row context without the row columns. Used in debug log reporting.
        """
        return {k: v for k, v in self.get_context().items()
                if k not in self.parent.spec.variables}

    def __str__(self):
        return row_to_str(self, self.parent.column_widths)

    def __repr__(self):
        return str(self)

    def __getitem__(self, idx):
        """
        Get column `idx` value of this row.
        """
        return self.var_vals[self.vars[idx].name]

    def __iter__(self):
        """
        Iterate over row values in order of variable/column definition.
        """
        return iter((self.var_vals[v.name] for v in self.vars))

    def __eq__(self, other):
        return self.var_vals == other.var_vals
