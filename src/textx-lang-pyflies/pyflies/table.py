from typing import List
import pyflies
from .exceptions import PyFliesException
from .scope import ScopeProvider
from .lang.pyflies import ModelElement
from .evaluated import EvaluatedBase


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


class TableInst(EvaluatedBase):
    """
    Instance of a table with expanded conditions table and evaluated phases
    """


class ExpTable(ModelElement):
    """
    Represents fully expanded and evaluated Condition table.
    """
    def __init__(self, table_inst):
        self.parent = table_inst
        self.column_widths = None
        self.rows = []

    def calculate_column_widths(self):
        self.column_widths = get_column_widths(self.parent.variables, self.rows)

    def calc_phases(self):
        """
        Evaluates condition components specification from the associated condition
        table for each trial phase.  After evaluation each row will have
        connected appropriate, evaluated components instances.
        """
        for row in self.rows:
            row.calc_phases()

    def header_str(self):
        return header_str(self.parent.variables, self.column_widths)

    def __str__(self):
        return table_to_str(self.parent.variables, self.rows, self.column_widths)

    def __getitem__(self, idx):
        return self.rows[idx]

    def __iter__(self):
        return iter(self.rows)

    def __eq__(self, other):
        return self.rows == other.rows


class ExpTableRow(ModelElement, ScopeProvider):
    def __init__(self, table: ExpTable, exps: List['pyflies.model.Expression']):
        self.parent = table
        self.exps = exps
        table.rows.append(self)

        # Create variable assignments needed by ScopeProvider.
        # We inherit all standard scope provider mechanics in reference
        # resolving and variable calculation.
        from .lang.pyflies import VariableAssignment
        self.vars = []
        for name, value in zip(self.parent.parent.variables, self.exps):
            self.vars.append(VariableAssignment(self, name=name, value=value))

        # Trial phases
        self.ph_fix = None
        self.ph_exec = None
        self.ph_error = None
        self.ph_correct = None

        # All comp time spec together
        self.comp_times = []

    def calc_phases(self):
        """
        Evaluate condition components specification for each phase of this trial.
        If condition is True evaluate components specs and attach to this row.
        """
        for phase in ['fix', 'exec', 'error', 'correct']:
            context = self.get_context({phase: True})

            test = self.parent.parent.parent
            # Evaluate test variables in the context of this row
            test.eval(context)

            # Keep full context on the row for debugging purposes
            # e.g. export to log
            self.var_vals.update(self.get_context())

            for cond_comp in test.components_cond:
                try:
                    cond_val = cond_comp.condition.eval(context)
                except PyFliesException:
                    cond_val = False

                if cond_val is True:
                    comp_insts = []
                    last_comp = None
                    for comp_time in cond_comp.comp_times:
                        comp_time_inst = comp_time.eval(context, last_comp)
                        comp_insts.append(comp_time_inst)
                        self.comp_times.append(comp_time_inst)
                        last_comp = comp_time
                    setattr(self, f'ph_{phase}', comp_insts)
                    break

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
