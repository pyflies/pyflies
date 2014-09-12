"""
Generator for Expyriment library.
"""

name = "Expyriment"
description = "Expyriment -A Python library for cognitive and neuroscientific experiments"

import jinja2
import re
from itertools import ifilter
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


def generate(target_folder, model, responses, params):
    """
    Args:
        target_folder(str): A name of the folder where generated code should
        be placed.
        model(pyFlies model):
        responses(dict): A map of model responses to platform specific
            responses.
        params(dict): A map of platform specific parameters.
    """

    # Transform stimuli sizes and positions
    for b in model.blocks:
        if b._typename == "TestType":
            for cs in b.stimuli.condStimuli:
                s = cs.stimulus
                if s._typename in ['Shape', 'Image']:
                    # TODO: Transform coordinates and sizes
                    pass

    def striptabs(s):
        return re.sub(r'^[ \t]+', '', s, flags=re.M)

    # Find this target
    target = next(ifilter(lambda t: t.name == "Expyriment", model.targets))

    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(join(dirname(__file__), 'templates')))
    jinja_env.filters['striptabs'] = striptabs
    template = jinja_env.get_template('expyriment.py.template')

    with open(join(target_folder, 'test.py'), 'w') as f:
        f.write(template.render(m=model, target=target, color_map=color_map))
