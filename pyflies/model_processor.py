from itertools import ifilter
from textx.exceptions import TextXSemanticError


def pyflies_model_processor(model, metamodel):
    """
    Validates model, evaluates condition matches in stimuli definitions
    and creates a map from each condition to a set of stimuli that matches.
    """

    # Post-processing is done for each test type
    for e in model.elements:
        if e.__class__.__name__ == "TestType":
            condition_map = {}
            for var in e.conditions.varNames:
                condition_map[var] = []
                conds = len(condition_map)
            for c in e.conditions.conditions:

                # Check if proper number of condition variables is specified
                if conds != len(c.conditionVars):
                    line, col = \
                        metamodel.parser.pos_to_linecol(c._position)
                    raise TextXSemanticError(
                        "There should be {} condition variables at {}".format(
                            conds, (line, col)), line=line, col=col)

                for idx, param_name in enumerate(e.conditions.varNames):
                    condition_map[param_name].append(c.conditionVars[idx])

            e.condition_map = condition_map

            def cond_matches(idx, c, exp):
                """
                Evaluates condition match expression.
                """
                if exp.__class__.__name__ == "EqualsExpression":
                    return condition_map[exp.varName][idx] == exp.varValue
                elif exp.__class__.__name__ == "AndExpression":
                    val = True
                    for op in exp.operand:
                        val = val and cond_matches(idx, c, op)
                    return val
                elif exp.__class__.__name__ == "OrExpression":
                    val = False
                    for op in exp.operand:
                        val = val or cond_matches(idx, c, op)
                    return val

                # This should not happen
                assert False

            # For each condition we iterate trough all stimuli
            # definitions and evaluate condition match. If the
            # condition evaluates to True stimulus is included
            # for condition.
            for idx, c in enumerate(e.conditions.conditions):
                c.stimuli_for_cond = []
                for s in e.stimuli.stimuli:
                    exp = s.conditionMatch.expression
                    if exp.__class__.__name__ == "AnyCondition" or\
                        (exp.__class__.__name__ == "OrdinalCondition" and
                         idx == exp.expression - 1) or\
                        (exp.__class__.__name__ == "ExpressionCondition" and
                            cond_matches(idx, c, exp.expression)):
                        c.stimuli_for_cond.append(s)

    # Extract experiment
    model.experiment = next(ifilter(
        lambda x: x.__class__.__name__ == "Experiment",
        model.elements), None)

    # Extract targets
    model.targets = list(ifilter(
        lambda x: x.__class__.__name__ == "Target",
        model.elements))

