import os
from textx import language, metamodel_from_file
from .model_processor import pyflies_model_processor

__version__ = "0.4.0.dev"


@language('pyflies', '*.pf')
def pyflies_language():
    "pyflies language"
    current_dir = os.path.dirname(__file__)
    mm = metamodel_from_file(os.path.join(current_dir, 'pyflies.tx'))

    # Here if necessary register object processors or scope providers
    # http://textx.github.io/textX/stable/metamodel/#object-processors
    # http://textx.github.io/textX/stable/scoping/
    mm.register_model_processor(pyflies_model_processor)

    return mm
