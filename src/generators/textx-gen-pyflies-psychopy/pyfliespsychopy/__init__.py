import re
import click
from os.path import basename, splitext, join, dirname
from textx import generator
from textxjinja import textx_jinja_generator

__version__ = "0.1.0.dev"


@generator('pyflies', 'psychopy')
def pyflies_generate_psychopy(metamodel, model, output_path, overwrite, debug,
                              **custom_args):
    "Generator for generating PsychoPy code from pyFlies descriptions"

    template_file = join(dirname(__file__), 'templates', 'main.py.jinja')

    if output_path is None:
        output_file = basename(splitext(model._tx_filename)[0]) + '.py'
    else:
        output_file = output_path

    settings = {}
    for target in model.targets:
        if target.name.lower() == 'psychopy':
            for ts in target.settings:
                settings[ts.name] = ts.value

    visited = set()
    unresolved = set()
    def recursive_resolve(obj):
        """
        Find all unresolved symbols in the experiment model and replace with
        value from target settings. Collect all that cant be replaced to issue
        warning to the user.
        """
        if id(obj) in visited:
            return
        visited.add(id(obj))
        try:
            attrs = vars(obj).items()
        except TypeError:
            if type(obj) is list:
                attrs = enumerate(obj)
            else:
                return

        for idx, attr in attrs:
            print(attr.__class__.__name__)
            if attr.__class__.__name__ == 'VariableRef':
                if attr.name in settings:
                    if type(obj) is list:
                        obj[idx] = settings[attr.name]
                    else:
                        setattr(obj, idx, settings[attr.name])
                else:
                    unresolved.add(attr.name)
            recursive_resolve(attr)
    recursive_resolve(model)

    unresolved -= {'fix', 'exec', 'error', 'correct'}

    if unresolved:
        click.echo('Warning: these symbols where not resolved by '
                'the target configuration: {}'.format(unresolved))

    filters = {
        'striptabs': striptabs,
        'type': typ,
        'color': color,
        'point': point,
        'size': size,
    }

    config = {'m': model, 'settings': settings}


    # call the generator
    textx_jinja_generator(template_file, output_file, config, overwrite, filters)


# Jinja filters

def striptabs(s):
    return re.sub(r'^[ \t]+', '', s, flags=re.M)


def typ(obj):
    return obj.__class__.__name__


def color(obj):
    """
    Mapping of color names
    """
    return obj

def point(obj):
    """
    Mapping of points
    """
    return obj

def size(obj):
    """
    Mapping of sizes
    """
    return obj
