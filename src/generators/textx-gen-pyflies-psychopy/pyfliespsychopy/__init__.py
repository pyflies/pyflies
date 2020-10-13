import re
import click
import datetime
from os.path import basename, splitext, join, dirname
from textx import generator
from textxjinja import textx_jinja_generator

from pyflies.lang.common import Symbol, Point

__version__ = "0.1.0.dev"


# Settings from the model target configuration
settings = {}


@generator('pyflies', 'psychopy')
def pyflies_generate_psychopy(metamodel, model, output_path, overwrite, debug,
                              **custom_args):
    "Generator for generating PsychoPy code from pyFlies descriptions"

    global settings

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
        value from target settings. Collect all that can't be replaced to issue
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

    default_settings = {
        'resolution': '(1024, 768)',
    }

    for dsn, ds in default_settings.items():
        if dsn not in settings:
            settings[dsn] = ds

    filters = {
        'comp_type': comp_type,
        'param_used': param_used,
        'param_name': param_name,
        'param_value': param_value,
        'striptabs': striptabs,
        'type': typ,
        'color': color,
        'point': point,
        'size': size,
        'duration': duration,

    }

    now = datetime.datetime.now()
    now = now.strftime('%Y-%m-%d %H:%M:%S')
    config = {'m': model, 'settings': settings, 'now': now}

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
    return "'{}'".format(str(obj))


def point(obj):
    """
    Mapping of points/positions
    """
    p = {
        'left': (-0.5, 0),
        'right': (0.5, 0),
        'up': (0, 0.5),
        'down': (0, -0.5),
     }.get(str(obj))

    if p is None:
        return (size(obj.x), size(obj.y))
    return p



def size(obj):
    """
    Mapping of sizes
    """
    return obj / 100


def duration(obj):
    """
    Mapping of durations to seconds
    """
    return obj / 1000

def comp_type(comp):
    """
    Mapping of component types
    """
    return {
        'text': 'visual.TextStim',
        'circle': 'visual.Circle',
        'rectangle': 'visual.Rect',
        'cross': 'visual.ShapeStim',
        'line': 'visual.Line',
        'image': 'visual.ImageStim',
        'sound': 'sound.SoundPTB',
        'audio': 'sound.SoundPTB',
        'mouse': 'event.Mouse',
        'key': 'event.Key',
    }.get(comp.type.name, 'UNEXISTING_COMPONENT')


def param_used(param):
    """
    A predicate to tell if the given parameter is used by the PsychoPy.
    """
    comp = param.parent.type.name
    if comp == 'text':
        # fillColor is not used for text
        return {
            'fillColor': False,
        }.get(param.name, True)
    return True


def param_name(param):
    """
    Mapping of component parameter names.
    """
    comp = param.parent.type.name
    return {
        'position': 'pos',

        'size': {
            # Special handling for TextStim
            'text': 'height'
        }.get(comp, 'size'),

        'color': {
            # Special handling for TextStim
            'text': 'color'
        }.get(comp, 'lineColor'),

        'from': 'start',
        'to': 'end',

        'file': {
            'image': 'image',
            'sound': 'value',
            'audio': 'value',
            }.get(comp),

        'freq': 'value',

    }.get(param.name, param.name)


def param_value(param):
    """
    Mapping of component values.
    """
    value = param.value

    # If the value is symbol check target mapping configuration
    if type(value) is Symbol:
        if str(value) in settings:
            return "'{}'".format(settings[str(value)])

    if type(param.value) is Point or param.name == 'position':
        return point(param.value)
    elif param.name == 'size':
        return size(param.value)
    elif type(param.value) in [str, Symbol]:
        return "'{}'".format(param.value)

    return param.value
