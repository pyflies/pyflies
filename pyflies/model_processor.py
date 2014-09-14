from textx.exceptions import TextXSemanticError


# Values for descriptive sizes
sizes = {
    'tiny': 10,
    'small': 20,
    'normal': 30,
    'large': 50,
    'huge': 100
}

# Possible colors
colors = ["white", "black", "red", "yellow", "green", "blue", "grey"]

# Values for descriptive positions
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

# Stimuli params that can reference condition variable value
resolvable = {
    'dmin': int,
    'color': str,
    'fillcolor': str,
    'text': str,
    'width': int,
    'x': int,
    'lineWidth': int
}

defaults = {
    'color': "white",
    'fillcolor': "white",
    'width': "normal",
    'x': "center",
    'lineWidth': 1
    # dmin, dmax inherits from testtype
}


def resolve(stimulus, test_type, condition, metamodel):
    """
    Create a new stimulus with all parameter references resolved for
    current conditions, and defaults set.
    """
    # Instantiate stimuli meta-class
    s = metamodel[stimulus._typename]()

    # Copy all attributes
    for attr in s.__class__._attrs:
        setattr(s, attr, getattr(stimulus, attr))
    s._position = stimulus._position

    # Try to resolve all resolvable stimuli parameters
    for p in resolvable:
        if hasattr(s, p):
            param_value = getattr(s, p)
            # If value is equal to some of
            # condition variable names use
            # the current value of that variable
            if param_value in test_type.conditions.varNames:
                setattr(s, p, condition.varValues[
                    test_type.conditions.varNames.index(param_value)])

    # Set defaults
    for attr in s.__class__._attrs:
        attr_val = getattr(s, attr)
        if not attr_val:
            def_val = None
            if attr in defaults:
                def_val = defaults[attr]
            else:
                # Special case
                # Inherit from stimuli definition
                if attr in ['dmin', 'dmax']:
                    def_val = getattr(test_type.stimuli, attr)
                elif attr not in ['height', 'y']:
                    # This should not happen
                    assert 0, "No default for attribute '{}' test type '{}'"\
                        .format(attr, test_type.name)
            if def_val is not None:
                setattr(s, attr, def_val)

    # Convert resolvable to a proper type and descriptive value
    for p, t in resolvable.items():
        if hasattr(s, p):
            val = getattr(s, p)
            try:
                val = t(val)
            except ValueError:
                if p not in ['x', 'width']:
                    line, col = \
                        metamodel.parser.pos_to_linecol(stimulus._position)
                    raise TextXSemanticError(
                        "Parameter {} is not of type '{}' at {}".format(
                            p, t.__name__, (line, col)), line=line, col=col)
                else:
                    # Check if descriptive name is given
                    if p == 'x':
                        pos = getattr(s, 'x')
                        if pos in positions:
                            x, y = positions[pos]
                            s.x = x
                            s.y = y
                        else:
                            line, col = \
                                metamodel.parser.pos_to_linecol(
                                    stimulus._position)
                            raise TextXSemanticError(
                                "Invalid position '{}' at {}".format(
                                    pos, (line, col)), line=line, col=col)
                    elif p == 'width':
                        width = getattr(s, 'width')
                        if width in sizes:
                            size = sizes[width]
                            s.width = size
                            s.height = size
                        else:
                            line, col = \
                                metamodel.parser.pos_to_linecol(
                                    stimulus._position)
                            raise TextXSemanticError(
                                "Invalid size '{}' at {}"
                                .format(width, (line, col)),
                                line=line, col=col)
                    else:
                        # This should not happen
                        assert 0, "Unknown param {}".format(p)


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
            if "response" not in e.conditions.varNames:
                line, col = \
                    metamodel.parser.pos_to_linecol(e.conditions._position)
                raise TextXSemanticError(
                    "There must be condition variable named 'response' at {}"
                    .format((line, col)), line=line, col=col)

            # Default for timings
            if e.stimuli.dmin == 0:
                e.stimuli.dmin = 1000

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
                    stimuli = s.stimuli

                    if (exp._typename == "FixedCondition" and
                            exp.expression == "all") or\
                        (exp._typename == "OrdinalCondition" and
                         idx == exp.expression - 1) or\
                        (exp._typename == "ExpressionCondition" and
                            cond_matches(idx, c, exp.expression)):

                        # For each stimuli create a new instance
                        # with all params resolved
                        stimuli_for_match = []
                        for stimulus in stimuli:
                            stimuli_for_match.append(
                                resolve(stimulus, e, c, metamodel))

                        c.stimuli_for_cond.append(stimuli_for_match)

            # Find special sitmuli if any (error, correct, fixation)
            e._error = []
            e._correct = []
            e._fix = []
            for s in e.stimuli.condStimuli:
                exp = s.conditionMatch.expression
                if exp._typename == "FixedCondition":
                    stimuli = s.stimuli
                    if exp.expression == "error":
                        e._error.append(stimuli)
                    elif exp.expression == "correct":
                        e._correct.append(stimuli)
                    elif exp.expression == "fixation":
                        e._fix.append(stimuli)



