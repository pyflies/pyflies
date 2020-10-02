from os.path import dirname, abspath, join
from textx import generator
from textxjinja import textx_jinja_generator


@generator('pyflies', 'log')
def pyflies_log_generator(metamodel, model, output_path, overwrite, debug, **custom_args):
    """Generator for log/debug files."""

    this_folder = dirname(abspath(__file__))
    template_file = join(this_folder, 'debug.log.jinja')

    tests = [t for t in model.blocks if t.__class__.__name__ == 'Test']
    screens = [t for t in model.blocks if t.__class__.__name__ == 'Screen']

    config = {'m': model,
              'tests': tests,
              'screens': screens}

    if not output_path:
        output_path = dirname(abspath(model._tx_filename))

    textx_jinja_generator(template_file, output_path, config, overwrite)