from textx.exceptions import TextXSemanticError
from pyflies.generators import generator_names


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
    'radius': int,
    'color': str,
    'fillColor': str,
    'text': str,
    'width': int,
    'x': int,
    'lineWidth': int
}

defaults = {
    'start': 0,
    'duration': 3000,
    'target': False,
    'keep': False,
    'color': "white",
    'fillColor': "black",
    'width': "normal",
    'radius': "normal",
    'x': "center",
    'size': 15,     # Default font size
    'lineWidth': 1
}


def resolve(stimulus, test_type, condition, metamodel):
    """
    Create a new stimulus with all parameter references resolved for
    current conditions, and defaults set.
    """

    def resolve_condition_var_references(s):
        # Try to resolve all resolvable stimuli parameters
        # using values from conditions table.
        if condition:
            for p in resolvable:
                if hasattr(s, p):
                    param_value = getattr(s, p)
                    # If value is equal to some of
                    # condition variable names use
                    # the current value of that variable
                    if param_value in test_type.conditions.varNames:
                        setattr(s, p, condition.varValues[
                                test_type.conditions.varNames.index(
                                    param_value)])

    def set_default_values(s):
        """
        Set default values for all stimuli parameters not defined in the model.
        """
        for attr in s.__class__._attrs:
            attr_val = getattr(s, attr)
            if not attr_val:
                def_val = None
                if attr == 'duration':
                    # Special case
                    # Inherit from stimuli definition if exists or
                    # create new Duration object with default value.
                    if test_type.stimuli.duration:
                        def_val = test_type.stimuli.duration
                    else:
                        def_val = metamodel['Duration']()
                        def_val.value = defaults['duration']
                elif attr == 'start':
                    # Special case
                    # Complex type. Create instance
                    def_val = metamodel['Start']()
                    def_val.value = defaults['start']
                elif attr in ['_from', 'to'] and \
                        s.__class__.__name__ == 'Point':
                    # Line parameters
                    def_val = metamodel['Point']()
                    def_val.x = 0
                    def_val.y = 0
                elif attr in defaults:
                    def_val = defaults[attr]
                elif attr not in ['_from', 'to', 'value', 'height', 'y']:
                    # This should not happen
                    assert 0, "No default for attribute '{}' " \
                            ", stimulus type  '{}'" \
                            "test type '{}'" \
                            .format(attr, s.__class__.__name__,
                                    test_type.name)
                if def_val is not None:
                    setattr(s, attr, def_val)

    def convert_descriptive_values(s):
        """
        Convert from descriptive to real values.
        """
        # Convert resolvable from descriptive values to real values.
        for p, t in resolvable.items():
            if hasattr(s, p):
                val = getattr(s, p)
                try:
                    val = t(val)
                    # Convert value to proper type.
                    setattr(s, p, val)
                except TypeError:
                    # If not string or a number than it is some complex type
                    pass
                except ValueError:
                    # Only size and position may be given descriptively
                    if p not in ['x', 'width', 'radius']:
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
                        elif p == 'radius':
                            radius = getattr(s, 'radius')
                            if radius in sizes:
                                s.radius = sizes[radius]
                            else:
                                line, col = \
                                    metamodel.parser.pos_to_linecol(
                                        stimulus._position)
                                raise TextXSemanticError(
                                    "Invalid radius '{}' at {}"
                                    .format(radius, (line, col)),
                                    line=line, col=col)
                        else:
                            # This should not happen
                            assert 0, "Unknown param {}".format(p)

    # Instantiate stimulus meta-class
    s = metamodel[stimulus._typename]()

    # Copy all attributes
    for attr in s.__class__._attrs:
        setattr(s, attr, getattr(stimulus, attr))
    s._position = stimulus._position

    resolve_condition_var_references(s)
    set_default_values(s)
    convert_descriptive_values(s)

    return s


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

            # Default duration
            if e.stimuli.duration is None:
                default_duration = metamodel['Duration']()
                default_duration.value = 3000
                e.stimuli.duration = default_duration

            # Create map of condition variables to collect their values.
            condvar_values = {}
            for var in e.conditions.varNames:
                condvar_values[var] = []

            for c in e.conditions.conditions:

                # Check if proper number of condition variable values is
                # specified
                if len(condvar_values) != len(c.varValues):
                    line, col = \
                        metamodel.parser.pos_to_linecol(c._position)
                    raise TextXSemanticError(
                        "There must be {} condition variable values at {}"
                        .format(len(condvar_values), (line, col)),
                        line=line, col=col)

                # Fill the map of condition variable values for this condition.
                for idx, param_name in enumerate(e.conditions.varNames):
                    condvar_values[param_name].append(c.varValues[idx])

            # Attach the map of values to the test to be used in
            # condition match expression evaluation and in generator
            # templates.
            e.condvar_values = condvar_values

            def cond_matches(idx, c, exp):
                """
                Recursively evaluates condition match expression.
                """
                if exp._typename == "EqualsExpression":
                    return condvar_values[exp.varName][idx] == exp.varValue
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

            # We create, for each condition, a list
            # of stimuli that should be presented in the condition.
            # This list is stimuli_for_cond accessible on each
            # Condition object.
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

            # Find special stimuli if any (error, correct, fixation)
            e.error = []
            e.correct = []
            e.fix = []
            for s in e.stimuli.condStimuli:
                exp = s.conditionMatch.expression
                if exp._typename == "FixedCondition" and\
                        exp.expression in ["error", "correct", "fixation"]:
                    stimuli = [resolve(st, e, None, metamodel)
                               for st in s.stimuli]
                    if exp.expression == "error":
                        e.error = stimuli
                    elif exp.expression == "correct":
                        e.correct = stimuli
                    elif exp.expression == "fixation":
                        e.fix = stimuli

    # Check targets
    for target in model.targets:
        if target.name not in generator_names():
            line, col = \
                metamodel.parser.pos_to_linecol(target._position)
            raise TextXSemanticError(
                "Unknown target '{}' at {}. Valid targets are {}"
                .format(target.name, (line, col), list(generator_names())),
                line=line, col=col)
