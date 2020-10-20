import re
import click
import datetime
import pprint
from itertools import chain
from os.path import basename, splitext, join, dirname
from textx import generator
from textxjinja import textx_jinja_generator

from pyflies.exceptions import PyFliesException
from pyflies.tools import resolve_params
from pyflies.lang.common import Symbol, Point

__version__ = "0.1.0.dev"


# These are settings that can be used in the `target` configuration. A default
# value will be used if a setting is not provided. These settings can be
# referenced as variables in all expressions in the pyFlies model.
default_settings = {
    'left': (-0.5, 0),
    'right': (0.5, 0),
    'up': (0, 0.5),
    'down': (0, -0.5),

    # In the context of keyboard component map directions to keys
    'keyboard.left': 'left',
    'keyboard.right': 'right',
    'keyboard.up': 'up',
    'keyboard.down': 'down',

    'fullScreen': False,
    'resolution': (1024, 768),
    'background': 'black',
    'frameTolerance': 0.001,
    'soundBackend': 'backend_ptb.SoundPTB',
}

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

    settings = dict(default_settings)
    for target in model.targets:
        if target.name.lower() == 'psychopy':
            for ts in target.settings:
                settings[ts.name] = ts.value

    unresolved = resolve_params(model, settings)
    if unresolved:
        click.echo('Warning: these symbols where not resolved by '
                'the target configuration: {}'.format(unresolved))

    filters = {
        'comp_type': comp_type,
        'comp_default_params': comp_default_params,
        'pprint_trial': pprint_trial,
        'type': typ,
        'duration': duration,
        'mouse_targets': mouse_targets,
        'keyboard_keys': keyboard_keys,
    }

    now = datetime.datetime.now()
    now = now.strftime('%Y-%m-%d %H:%M:%S')
    config = {'m': model, 's': settings, 'now': now}

    # call the generator
    textx_jinja_generator(template_file, output_file, config, overwrite, filters)


# Jinja filters and mappings pyFlies -> PsychoPy

def pretty(obj, indent=0):
    p = ''
    sindent = ' ' * indent
    if isinstance(obj, dict):
        p += '{' + ',\n{}'.format(sindent).join(["'{}': {}".format(k, pretty(v, indent + 4))
                                                 for k, v in obj.items()]) + '}'
    elif isinstance(obj, list):
        p += '[\n{}'.format(sindent) + \
            ',\n{}'.format(sindent).join([pretty(x, indent + 4) for x in obj]) + ']'
    else:
        p += str(obj)
    return p

def pprint_trial(trial):
    trial_data = {}
    for phase in ['ph_fix', 'ph_exec', 'ph_error', 'ph_correct']:
        phase_comps = getattr(trial, phase)
        if phase_comps:
            trial_data[phase] = []
            for comp_time in phase_comps:
                cdata = {
                    'inst': comp_time.component.name,
                    'type': '\'{}.{}\''.format(
                        comp_time.component.type.extends[0].name,
                        comp_time.component.type.name),
                    'at': duration(comp_time.at),
                    'duration': duration(comp_time.duration)
                }
                cdata['params'] = {}
                for param in comp_time.component.params:
                    if not param.is_constant:
                        cdata['params'][param_name(param)] = param_value(param)
                trial_data[phase].append(cdata)

    a = pretty(trial_data, 8)
    return a


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
    return (coord(obj.x), coord(obj.y))


def coord(obj):
    """
    Scaling of coordinates.  pyFlies uses Descartes coordinates [-100, 100]
    while PsychoPy uses [-1, 1].
    """
    return obj / 100


def duration(obj):
    """
    Mapping of durations to seconds. pyFlies uses ms.
    """
    return obj / 1000

def comp_type(comp):
    """
    Mapping of component types
    """
    target_comp = {
        'text': 'visual.TextStim',
        'circle': 'visual.Circle',
        'rectangle': 'visual.Rect',
        'cross': 'visual.ShapeStim',
        'line': 'visual.Line',
        'image': 'visual.ImageStim',
        'sound': 'sound.%s' % settings['soundBackend'],
        'audio': 'sound.%s' % settings['soundBackend'],
        'mouse': 'event.Mouse',
        'keyboard': 'keyboard.Keyboard',
    }.get(comp.type.name)

    assert target_comp is not None, \
        'No mapping for component {}'.format(comp.type.name)

    return target_comp


def as_str(o):
    return '\'{}\''.format(o)

def default_params(comp):
    """
    Returns a string of default parameters used by the component
    """
    dparams = []
    if comp.type.does_extend('visual'):
        dparams = [('win', 'win'), ('name', as_str(comp.name))]
        if comp.type.name == 'cross':
            dparams.append(('vertices', as_str('cross')))
    return dparams


def comp_default_params(comp):
    """
    Returns a string of default component parameters for component initialization.
    """
    return ', '.join(['{}={}'.format(name, value)
                      for name, value in
                      chain(default_params(comp),
                            ((param_name(p), param_value(p))
                             for p in params_used(params_constant(comp.params))))])

def params_constant(params):
    """
    Filter list of parameters and return only constant.
    """
    return [p for p in params if p.is_constant]

def params_used(params):
    """
    Filter list and return only used params for the component
    """
    return [p for p in params if param_used(p)]


def param_used(param):
    """
    A predicate to tell if the given parameter is used by the PsychoPy.
    """
    comp = param.parent.type.name
    return {
        # fillColor is not used for text
        'text': {
            'fillColor': False,
        }.get(param.name, True),

        'image': {
            'fillColor': False,
            'color': False,
        }.get(param.name, True),

        # valid response is not used by Keyboard component
        'keyboard': {
            'valid': False,
        }.get(param.name, True),

        'mouse': {
            'target': False,
        }.get(param.name, True),
    }.get(comp, True)


def param_name(param):
    """
    Mapping of component parameter names.
    """
    # For injected parameters we won't do any mapping
    if not hasattr(param, 'parent'):
        return param.name

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
        'content': 'text',

        'file': {
            'image': 'image',
            'sound': 'value',
            'audio': 'value',
            }.get(comp),

        'freq': 'value',

    }.get(param.name, param.name)


def param_value(param):
    """
    Mapping of component parameter values.
    """
    # For injected parameters we won't do any mapping
    if not hasattr(param, 'parent'):
        return param.value

    value = param.value
    comp = param.parent.type.name

    if type(param.value) is Point:
        return point(param.value)
    elif type(param.value) in [int, float]:
        # Numerical values
        # By default return as is if not recognized
        # as coordinate by param name and comp type
        return {
            'size': coord(param.value),
            'radius': coord(param.value),
        }.get(param.name, param.value)

    elif type(param.value) in [str, Symbol]:
        # Strings and symbols map to quoted strings
        return as_str(param.value)

    elif type(param.value) in [tuple, bool]:
        # For bools and points resolved through default settings
        return param.value

    raise PyFliesException('Unrecognized parameter '
                           'type "{}" for parameter "{}"'
                           .format(type(param.value), param.name))


def mouse_targets(comp):
    """
    Return a list of target components names for this mouse.
    """
    target_param = [c for c in comp.params if c.name == 'target']
    if target_param:
        value = target_param[0].value
        if type(value) is list:
            return [v.name for v in value]
        elif value.name != 'none':
            return [value.name]
    return []


def keyboard_keys(comp):
    """
    Return a list of valid keyboard keys.
    """
    q = as_str('quit')
    valid_param = [c for c in comp.params if c.name == 'valid']
    if valid_param:
        value = valid_param[0].value
        if type(value) is list:
            return [as_str(str(v)) for v in value] + [q]
        elif value.name != 'none':
            return [as_str(value.name), q]
    return [q]


