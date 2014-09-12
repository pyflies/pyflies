from textx.exceptions import TextXSemanticError


sizes = {
    'tiny': 10,
    'small': 20,
    'normal': 30,
    'large': 50,
    'huge': 100
}

positions = {
    "center": (0, 0),
    "left": (-50, 0),
    "right": (50, 0),
    "top": (0, 50),
    "bottom": (0, -50),
    "topLeft": (-50, 50),
    "topRight": (50, 50),
    "bottomLeft": (-50, -50),
    "bottomRight": (50, -50),
    "farLeft": (-100, 0),
    "farRight": (100, 0),
    "farTop": (0, 100),
    "farBottom": (0, -100),
    "farBottomLeft": (-100, -100),
    "farBottomRight": (100, -100),
    "farTopLeft": (-100, 100),
    "farTopRigh": (100, 100)
}


def stimulus_default(stimulus, metamodel):
    """
    Sets default value for stimulus.
    """
    # Default shape color
    if stimulus._typename in ["Text", "Shape"]:
        if stimulus.color is None:
            stimulus.color = "white"

    if stimulus._typename in ["Text", "Shape", "Image"]:

        # Instantiate meta-classes if not given by the user
        if not stimulus.position:
            stimulus.position = metamodel['Position']()
        if not stimulus.size:
            stimulus.size = metamodel['Size']()

        if not stimulus.position.descriptive and \
                stimulus.position.x == 0 and \
                stimulus.position.y == 0:
            stimulus.position.descriptive = "center"
        if stimulus.position.descriptive:
            stimulus.position.x, stimulus.position.y = \
                positions[stimulus.position.descriptive]
        if not stimulus.size.descriptive and \
                stimulus.size.x == 0 and stimulus.size.y == 0:
            stimulus.size.descriptive = "normal"
        if stimulus.size.descriptive:
            stimulus.size.x = stimulus.size.y = \
                stimulus.size.both = \
                sizes[stimulus.size.descriptive]
    elif stimulus._typename in ["Audio", "Sound"]:
        stimulus.duration = 300

    if stimulus.duration == 0:
        stimulus.duration = 1000

def pyflies_model_processor(model, metamodel):
    """
    Validates model, evaluates condition matches in stimuli definitions,
    creates a map from each condition to a set of stimuli that matches and
    sets default values.
    """

    # Post-processing is done for each test type
    for e in model.blocks:
        if e._typename == "TestType":

            # Check that there is a condition variable named "response"
            if not "response" in e.conditions.varNames:
                line, col = \
                    metamodel.parser.pos_to_linecol(e.conditions._position)
                raise TextXSemanticError(
                    "There must be condition variable named 'response' at {}".format(
                        (line, col)), line=line, col=col)

            condvar_map = {}
            for var in e.conditions.varNames:
                condvar_map[var] = []
                conds = len(condvar_map)
            for c in e.conditions.conditions:

                # Check if proper number of condition variables is specified
                if conds != len(c.varValues):
                    line, col = \
                        metamodel.parser.pos_to_linecol(c._position)
                    raise TextXSemanticError(
                        "There must be {} condition variables at {}".format(
                            conds, (line, col)), line=line, col=col)

                for idx, param_name in enumerate(e.conditions.varNames):
                    condvar_map[param_name].append(c.varValues[idx])

            e.condvar_map = condvar_map

            def cond_matches(idx, c, exp):
                """
                Evaluates condition match expression.
                """
                if exp._typename == "EqualsExpression":
                    return condvar_map[exp.varName][idx] == exp.varValue
                elif exp._typename == "AndExpression":
                    val = True
                    for op in exp.operand:
                        val = val and cond_matches(idx, c, op)
                    return val
                elif exp._typename == "OrExpression":
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
                for s in e.stimuli.condStimuli:
                    exp = s.conditionMatch.expression
                    stimulus = s.stimulus

                    if (exp._typename == "FixedCondition" and
                            exp.expression == "all") or\
                        (exp._typename == "OrdinalCondition" and
                         idx == exp.expression - 1) or\
                        (exp._typename == "ExpressionCondition" and
                            cond_matches(idx, c, exp.expression)):

                        # For Text stimuli, if the name of the text
                        # matches one of the condition params
                        # create one stimuli for each condition
                        if stimulus._typename == "Text":
                            if stimulus.text in e.conditions.varNames:
                                new_stim = metamodel['Text']()
                                new_stim.text = c.varValues[
                                    e.conditions.varNames.index(stimulus.text)]
                                new_stim.duration = stimulus.duration
                                new_stim.size = stimulus.size
                                new_stim.position = stimulus.position
                                new_stim.color = stimulus.color
                                stimulus = new_stim

                        c.stimuli_for_cond.append(stimulus)

            # Find special sitmuli if any (error, correct, fixation)
            e._error = []
            e._correct = []
            e._fix = []
            for s in e.stimuli.condStimuli:
                exp = s.conditionMatch.expression
                if exp._typename == "FixedCondition":
                    stimulus = s.stimulus
                    if exp.expression == "error":
                        e._error.append(stimulus)
                    elif exp.expression == "correct":
                        e._correct.append(stimulus)
                    elif exp.expression == "fixation":
                        e._fix.append(stimulus)

            # Default values for stimuli parameters
            for c in e.conditions.conditions:
                for s in e.stimuli.condStimuli:
                    stimulus = s.stimulus
                    stimulus_default(stimulus, metamodel)

            # Default values for stimuli for conditions
            for c in e.conditions.conditions:
                for stimulus in c.stimuli_for_cond:
                    stimulus_default(stimulus, metamodel)

            # Default timings
            if e.tmin == 0:
                e.tmin = 1500
            if e.tmax == 0:
                e.tmax = 3000




