import re
from os.path import basename, splitext, join, dirname
from textx import generator
from textxjinja import textx_jinja_generator

__version__ = "0.1.0.dev"


@generator('pyflies', 'psychopy')
def pyflies_generate_psychopy(metamodel, model, output_path, overwrite, debug,
                              **custom_args):
    "Generator for generating PsychoPy code from pyFlies descriptions"

    # template directory
    template_folder = join(dirname(__file__), 'templates')

    if output_path is None:
        output_path = dirname(model._tx_filename)

    file_name = basename(splitext(model._tx_filename)[0])
    config = {'m': model,
              'file_name': file_name,
              'responseMap': {}}

    for target in model.targets:
        if target.name.lower() == 'psychopy':
            if target.output:
                output_path = target.output

            for rm in target.responseMap:
                config['responseMap'][rm.name] = rm.target

            for tp in target.targetParam:
                config[tp.name] = tp.value

    filters = {
        'striptabs': striptabs,
        'duration': duration
    }

    # call the generator
    textx_jinja_generator(template_folder, output_path, config, overwrite, filters)


# Jinja filters

def striptabs(s):
    return re.sub(r'^[ \t]+', '', s, flags=re.M)


def duration(s):
    if type(s.duration) is int:
        print(s.shape)
    if type(s.duration) is list:
        return str(s.duration[0].value)
    if s.duration and s.duration.value:
        return str(s.duration.value)
    else:
        return "(%d, %d)" % (s.duration._from, s.duration.to)
