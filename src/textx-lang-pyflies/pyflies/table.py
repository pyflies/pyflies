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

    def eval_condition_stimuli(self, cond_stimuli_table):
        """
        Accepts a list of ConditionStimuli specification.  Iterates over all
        rows and applies each ConditionStimuli spec.
        """
        for idx, row in enumerate(self):
            for cond_stimuli in cond_stimuli_table:
                row.eval_condition_stimuli(cond_stimuli, idx)

    def __str__(self):
        return table_to_str(self.cond_table.variables, self, self.column_widths)


class ExpTableRow(list):
    def __init__(self, table, elements):
        self.table = table
        self.extend(elements if elements is not None else [])

        # Trial phases
        self.ph_fixation = None
        self.ph_execution = None
        self.ph_error = None
        self.ph_correct = None

    def eval_condition_stimuli(self, cond_stimuli, row_num):
        """
        Accepts ConditionStimuli specification, evaluates the condition and if
        it matches some of the phases, evaluated Stimuli are attached to the
        appropriate phase.
        """
        # 1. Evaluate conditon_stimuli.condition (Expression) in the context of
        # the current table row
        # cond_val = cond_stimuli.condition.eval()
        # if cond_val is True or cond_val == row_num:
        #     self.ph_execution = 

        # 2. If it is True or if evaluates to integer representing current row
        # number attach it to ph_execution. If it evaluates to some of the
        # symbols (fixation, error, correct) attach it to the appropriate phase.

    def eval(self, context=None):
        """
        All condition variable values must be evaluated to base
        values or symbols. Do this in loop because there can be
        forward references. If we pass a full loop and no value
        has been resolved we have cyclic reference
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
