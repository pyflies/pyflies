"""
Generator for Expyriment library.
"""

name = "Expyriment"
description = "Expyriment -A Python library for cognitive and neuroscientific experiments"

import jinja2
from os.path import join, dirname


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

    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(join(dirname(__file__), 'templates')))
    template = jinja_env.get_template('expyriment.py.template')

    with open(join(target_folder, 'test.py'), 'w') as f:
        f.write(template.render(m=model))
