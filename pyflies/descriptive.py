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
    'duration_from': 2000,
    'duration_to': 4000,
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
