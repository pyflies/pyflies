from textx import TextXSemanticError, get_children_of_type
# from pyflies.generators import generator_names


def processor(model, metamodel):

    for table in get_children_of_type('ConditionsTable', model):
        table.expand()


    return  #TODO: Rework/move checks from bellow

    # Post-processing is done for each test type
    for block in model.blocks:
        if block.__class__.__name__ == "TestType":

            # Check that there is a condition variable named "response"
            if "response" not in block.condVarNames:
                line, col = \
                    metamodel.parser.pos_to_linecol(
                        block.condVarNames[0]._tx_position)
                raise TextXSemanticError(
                    "There must be condition variable named 'response' at {}"
                    .format((line, col)), line=line, col=col)

            # Create default duration if not given.
            if block.duration is None:
                default_duration = metamodel['Duration']()
                default_duration.value = 0
                default_duration._from = defaults['duration_from']
                default_duration.to = defaults['duration_to']
                block.duration = default_duration

            # Create map of condition variables to collect their values.
            # For each variable name a list of values will be created
            # indexed by the condition ordinal number.
            condvar_values = {}
            for var in block.condVarNames:
                condvar_values[var] = []

            for c in block.conditions:

                # Check if proper number of condition variable values is
                # specified in the current condition.
                if len(block.condVarNames) != len(c.varValues):
                    line, col = \
                        metamodel.parser.pos_to_linecol(c._tx_position)
                    raise TextXSemanticError(
                        "There must be {} condition variable values at {}"
                        .format(len(condvar_values), (line, col)),
                        line=line, col=col)

                # Fill the map of condition variable values for this condition.
                for idx, var_name in enumerate(block.condVarNames):
                    condvar_values[var_name].append(c.varValues[idx])

            # Attach the map of values to the test to be used in
            # condition match expression evaluation and in generator
            # templates.
            block.condvar_values = condvar_values

            def cond_matches(idx, c, exp):
                """
                Recursively evaluates condition match expression.
                """
                if exp.__class__.__name__ == "EqualsExpression":
                    return condvar_values[exp.varName][idx] == exp.varValue
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

            # We create, for each condition, a list
            # of stimuli that should be presented in the condition.
            # This list is stimuli_for_cond accessible on each
            # Condition object.
            # For each condition we iterate trough all stimuli
            # definitions and evaluate condition match. If the
            # condition evaluates to True stimulus is included
            # for condition.
            for idx, c in enumerate(block.conditions):
                c.stimuli_for_cond = []
                for s in block.condStimuli:
                    exp = s.conditionMatch.expression
                    stimuli = s.stimuli

                    if (exp.__class__.__name__ == "FixedCondition"
                        and exp.expression == "all") or\
                        (exp.__class__.__name__ == "OrdinalCondition"
                         and idx == exp.expression - 1) or\
                        (exp.__class__.__name__ == "ExpressionCondition"
                         and cond_matches(idx, c, exp.expression)):

                        # For each stimuli create a new instance
                        # with all params resolved
                        stimuli_for_match = []
                        for stimulus in stimuli:
                            stimuli_for_match.append(
                                create_resolve_stimulus(stimulus,
                                                        block, c, metamodel))

                        c.stimuli_for_cond.append(stimuli_for_match)

            # Find special stimuli if any (error, correct, fixation)
            block.error = []
            block.correct = []
            block.fix = []
            for s in block.condStimuli:
                exp = s.conditionMatch.expression
                if exp.__class__.__name__ == "FixedCondition" and\
                        exp.expression in ["error", "correct", "fixation"]:
                    stimuli = [create_resolve_stimulus(st, block,
                                                       None, metamodel)
                               for st in s.stimuli]
                    if exp.expression == "error":
                        block.error = stimuli
                    elif exp.expression == "correct":
                        block.correct = stimuli
                    elif exp.expression == "fixation":
                        block.fix = stimuli

    # Check targets
    # FIXME: Target specs grammar should be provided by target generators
    # for target in model.targets:
    #     if target.name not in generator_names():
    #         line, col = \
    #             metamodel.parser.pos_to_linecol(target._tx_position)
    #         raise TextXSemanticError(
    #             "Unknown target '{}' at {}. Valid targets are {}"
    #             .format(target.name, (line, col), list(generator_names())),
    #             line=line, col=col)
