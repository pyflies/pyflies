import click
from os.path import dirname, abspath, join, splitext
from textx import generator
from textxjinja import textx_jinja_generator


@generator('pyflies', 'csv')
def pyflies_csv_generator(metamodel, model, output_path, overwrite, debug, **custom_args):
    """Generator for CSV files from pyFlies tables."""

    this_folder = dirname(abspath(__file__))
    template_file = join(this_folder, 'csv.jinja')

    if not model.flow or len([x for x in model.flow.insts
                              if x.__class__.__name__ == 'TestInst']) == 0:
        click.echo(click.style('ERROR: ', fg='red', bold=True), nl=False)
        click.echo('There are no table instances in the flow.'
                   ' Make sure you have `flow` block with at least one `execute`.')
        return

    click.echo('Warning: Only the first table from the flow will be saved to CSV.')

    # Find first table in the flow.
    table = [x for x in model.flow.insts
             if x.__class__.__name__ == 'TestInst'][0].table
    config = {'table': table}
    filters = {
        'csv_str': csv_str
    }

    if not output_path:
        output_path = splitext(model._tx_filename)[0] + '.csv'

    textx_jinja_generator(template_file, output_path, config, overwrite, filters=filters)


def csv_str(s):
    """
    Convert values s to content appropriate for CSV.
    E.g. add quotes for strings, apply various escaping.
    """
    if type(s) is str:
        return '"{}"'.format(s)
    return str(s)
