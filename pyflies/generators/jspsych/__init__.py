"""
Generator for `jsPsych`_ JavaScript library for behavioral experiments.
""" 

name = "jsPsych"
description = "jsPsych - A JavaScript library of online behavioral experiments"

from jinja2 import Template
from os.path import join, dirname


def generate(model, target_folder):
    """
    Generates a jsPsych experiment from the experiment model.

    Args:
        model(pyFlies model): A graph of Python objects defining experiment.
        target_folder(str): A name of the folder where generated code should
        be placed.
    """

    # Generate index template.
    with open(join(dirname(__file__), 'templates',
                   'index.html.template'), 'r') as f:
        index_template = f.read()

    template = Template(index_template)

    with open(join(target_folder, 'index.html'), 'w') as f:
        f.write(template.render(model=model))
