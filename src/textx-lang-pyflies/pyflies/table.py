from .exceptions import PyFliesException


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


def table_to_str(header, rows, column_widths):
    str_rep = row_to_str(header, column_widths)
    str_rep += '\n|' + '+'.join(['-' * x for x in column_widths]) + '|\n'
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


class ExpTable(list):
    """
    Represents fully expanded and evaluated Condition table.
    """
    def __init__(self, cond_table):
        self.cond_table = cond_table
        self.column_widths = None

    def new_row(self, elements=None):
        new_row = ExpTableRow(self, elements)
        self.append(new_row)
        return new_row

    def calculate_column_widths(self):
        self.column_widths = get_column_widths(self.cond_table.variables, self)

    def calc_phases(self):
        """
        Evaluates condition stimuli specification from the associated condition
        table for each trial phase.  After evaluation each row will have
        connected appropriate, evaluated stimuli instances.
        """
        for row in self:
            row.calc_phases()

    def __str__(self):
        return table_to_str(self.cond_table.variables, self, self.column_widths)


class ExpTableRow(list):
    def __init__(self, table, elements):
        self.table = table
        self.extend(elements if elements is not None else [])

        # Trial phases
        self.ph_fix = None
        self.ph_exec = None
        self.ph_error = None
        self.ph_correct = None

    def get_context(self, context):
        """
        Returns context containing passed context, this row variable values,
        and global scope (variable defined at model level) with priorities in
        the given order.
        """
        c = dict(zip(self.table.cond_table.variables, self))
        c.update(context)
        return self.table.cond_table.get_context(c)

    def calc_phases(self):
        """
        Evaluate condition stimuli specification for each phase of this trial.
        If condition is True evaluate stimuli specs and attach to this row.
        """
        for phase in ['fix', 'exec', 'error', 'correct']:
            context = self.get_context({phase: True})

            stim_specs = self.table.cond_table.parent.stimuli
            for sspec in stim_specs:
                try:
                    cond_val = sspec.condition.eval(context)
                except PyFliesException:
                    cond_val = False

                if cond_val is True:
                    stim_insts = []
                    last_stim = None
                    for stim in sspec.stimuli:
                        stim_inst = stim.eval(context, last_stim)
                        stim_insts.append(stim_inst)
                        last_stim = stim_inst
                    setattr(self, f'ph_{phase}', stim_insts)
                    break

    def eval(self, context=None):
        """
        All condition variable values must be evaluated to base values or
        symbols.  Do this in loop because there can be forward references.  If
        we pass a full loop and no value has been resolved we have cyclic
        reference
        """
        from .custom_classes import PostponedEval, Postpone, BaseValue, Symbol
        while True:
            all_resolved = all([not type(c) is PostponedEval for c in self])
            if all_resolved:
                break
            resolved = False
            for idx, c in enumerate(self):
                if type(c) is PostponedEval:
                    try:
                        cond_value = c.exp.eval(context)
                        self[idx] = cond_value
                        if type(cond_value) in [BaseValue, Symbol]:
                            context[self.table.cond_table.variables[idx]] = cond_value
                        resolved = True
                    except Postpone:
                        pass
            if not resolved:
                raise PyFliesException(
                    'Cyclic dependency in table. Row {}.'.format(self))

    def __str__(self):
        return row_to_str(self, self.table.column_widths)

    def __repr__(self):
        return str(self)
