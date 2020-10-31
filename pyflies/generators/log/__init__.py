import re
import datetime
from os.path import dirname, abspath, join, splitext
from textx import generator
from textxjinja import textx_jinja_generator


@generator('pyflies', 'log')
def pyflies_log_generator(metamodel, model, output_path, overwrite, debug, **custom_args):
    """Generator for log/debug files."""

    this_folder = dirname(abspath(__file__))
    template_file = join(this_folder, 'debug.log.jinja')

    tests = [t for t in model.routine_types if t.__class__.__name__ == 'TestType']
    screens = [t for t in model.routine_types if t.__class__.__name__ == 'ScreenType']

    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    config = {'m': model,
              'now': now,
              'tests': tests,
              'screens': screens}

    filters = {
        'unindent': unindent
    }

    if not output_path:
        output_path = splitext(model._tx_filename)[0] + '.pflog'

    textx_jinja_generator(template_file, output_path, config, overwrite, filters=filters)


def unindent(s):
    """
    Remove whitespaces from the beginning of each line of the string s.
    """
    return re.sub(r'\n[ \t]+', r'\n', s)
