"""
Generator for Expyriment library.
"""

name = "Expyriment"
description = "Expyriment -A Python library for cognitive and neuroscientific experiments"

from jinja2 import Template
from os.path import join, dirname

from pyflies.generators.util import flatten_experiment


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

    # Generate index template.
    with open(join(dirname(__file__), 'templates',
                   'expyriment.py.template'), 'r') as f:
        index_template = f.read()

    inst = flatten_experiment(model)

    template = Template(index_template)
    with open(join(target_folder, 'test.py'), 'w') as f:
        f.write(template.render(m=model, inst=inst))
