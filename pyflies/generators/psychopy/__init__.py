"""
Generator for PsychoPy software.
"""
import jinja2
import re
from os.path import join, dirname
from pyflies.generators.util import python_module_name

name = "PsychoPy"
description = "PsychoPy - Psychology software in Python"


def generate(model, target):
    """
    Args:
        model(pyFlies model):
        target(Target): An object that describe target platform.
    """

    # Transform stimuli sizes and positions
    for b in model.blocks:
        if b.__class__.__name__ == "TestType":
            for cs in b.condStimuli:
                for s in cs.stimuli:
                    if s.__class__.__name__ in ['Shape', 'Image']:
                        # TODO: Transform coordinates and sizes
                        pass

    # Create a map of response mapping for this target.
    response_map = {}
    for resp in target.responseMap:
        response_map[resp.name] = resp.target

    def striptabs(s):
        return re.sub(r'^[ \t]+', '', s, flags=re.M)

    def duration(s):
        if type(s.duration) is int:
            print(s.__class__.__name__)
            print(s.shape)
        if s.duration.value:
            return str(s.duration.value)
        else:
            return "(%d, %d)" % (s.duration._from, s.duration.to)

    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(join(dirname(__file__), 'templates')))
    jinja_env.filters['striptabs'] = striptabs
    jinja_env.filters['duration'] = duration
    template = jinja_env.get_template('psychopy.template')

    with open(join(target.output, python_module_name(model.name)), 'w') as f:
        f.write(template.render(m=model, target=target,
                response_map=response_map))
