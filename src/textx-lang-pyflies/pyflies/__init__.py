import os
from textx import language, metamodel_from_file
from .model_processor import processor
from .model import model_classes

__version__ = "0.4.0.dev"


@language('pyflies', '*.pf')
def pyflies_language():
    "A language for psychology experiments specification"
    current_dir = os.path.dirname(__file__)
    mm = metamodel_from_file(os.path.join(current_dir, 'pyflies.tx'), classes=model_classes)

    # Here if necessary register object processors or scope providers
    # http://textx.github.io/textX/stable/metamodel/#object-processors
    # http://textx.github.io/textX/stable/scoping/
    mm.register_model_processor(processor)

    return mm
