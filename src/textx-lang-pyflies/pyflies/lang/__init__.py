import os
from textx import language, metamodel_from_file
from .pyflies_processor import processor
from .pyflies import classes as pyflies_classes
from .components import classes as component_classes


@language('pyflies', '*.pf')
def pyflies_language():
    "A language for psychology experiments specification"
    current_dir = os.path.dirname(__file__)
    mm = metamodel_from_file(os.path.join(current_dir, 'pyflies.tx'),
                             classes=pyflies_classes)

    # Here if necessary register object processors or scope providers
    # http://textx.github.io/textX/stable/metamodel/#object-processors
    # http://textx.github.io/textX/stable/scoping/
    mm.register_model_processor(processor)

    return mm


@language('pyflies-comp', '*.pfc')
def pyflies_component_language():
    "A language for PyFlies component specification"
    current_dir = os.path.dirname(__file__)
    mm = metamodel_from_file(os.path.join(current_dir, 'components.tx'),
                             classes=component_classes)

    # Here if necessary register object processors or scope providers
    # http://textx.github.io/textX/stable/metamodel/#object-processors
    # http://textx.github.io/textX/stable/scoping/

    return mm
