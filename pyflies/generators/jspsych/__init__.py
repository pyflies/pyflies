"""
Generator for `jsPsych`_ JavaScript library for behavioral experiments.
"""

name = "jsPsych"
description = "jsPsych - A JavaScript library of online behavioral experiments"

from jinja2 import Template
from os.path import join, dirname


def generate(model, target):
    """
    Args:
        model(pyFlies model):
        target(Target): An object that describe target platform.
    """

    # Generate index template.
    with open(join(dirname(__file__), 'templates',
                   'index.html.template'), 'r') as f:
        index_template = f.read()

    template = Template(index_template)

    with open(join(target.output, 'index.html'), 'w') as f:
        f.write(template.render(model=model))
