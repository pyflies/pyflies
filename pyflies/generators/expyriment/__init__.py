"""
Generator for Expyriment library.
"""

name = "Expyriment"
description = "Expyriment -A Python library for cognitive and neuroscientific experiments"

import jinja2
import re
from os.path import join, dirname

color_map = {
    "white": "C_WHITE",
    "black": "C_BLACK",
    "grey": "C_GREY",
    "red":  "C_RED",
    "green": "C_GREEN",
    "blue": "C_BLUE",
    "yellow": "C_YELLOW"
}


def generate(model, target):
    """
    Args:
        model(pyFlies model):
        target(Target): An object that describe target platform.
    """

    # Transform stimuli sizes and positions
    for b in model.blocks:
        if b._typename == "TestType":
            for cs in b.stimuli.condStimuli:
                for s in cs.stimuli:
                    if s._typename in ['Shape', 'Image']:
                        # TODO: Transform coordinates and sizes
                        pass

    def striptabs(s):
        return re.sub(r'^[ \t]+', '', s, flags=re.M)

    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(join(dirname(__file__), 'templates')))
    jinja_env.filters['striptabs'] = striptabs
    template = jinja_env.get_template('expyriment.template')

    with open(join(target.output, 'test.py'), 'w') as f:
        f.write(template.render(m=model, target=target, color_map=color_map))
