import os
from os.path import join, dirname
from textx import language, metamodel_from_file, metamodel_for_language, scoping
import pyflies
from .pyflies_processor import processor
from .pyflies import classes as pyflies_classes
from .components import classes as component_classes


current_dir = dirname(__file__)


@language('pyflies', '*.pf')
def pyflies_language():
    "A language for psychology experiments specification"
    global_repo_provider = scoping.providers.PlainNameGlobalRepo()
    # global_provider = scoping.providers.PlainNameGlobalRepo()
    mm = metamodel_from_file(join(current_dir, 'pyflies.tx'),
                             classes=pyflies_classes, global_repository=True)

    # Load all component models
    component_folder = join(current_dir, '..', 'components')
    cmm = metamodel_for_language('pyflies-comp')
    import pdb; pdb.set_trace()
    for comp_file in os.listdir(component_folder):
        global_repo_provider.add_model(cmm.model_from_file(comp_file))

    # Here if necessary register object processors or scope providers
    # http://textx.github.io/textX/stable/metamodel/#object-processors
    # http://textx.github.io/textX/stable/scoping/
    mm.register_model_processor(processor)

    return mm


@language('pyflies-comp', '*.pfc')
def pyflies_component_language(**kwargs):
    "A language for PyFlies component specification"
    global_repo_provider = scoping.providers.PlainNameGlobalRepo()
    mm = metamodel_from_file(join(current_dir, 'components.tx'),
                             classes=component_classes, **kwargs)

    # Load base components which can be referenced in other component definition
    component_folder = join(dirname(pyflies.__file__), '..', 'components')
    global_repo_provider.add_model(mm.model_from_file(join(component_folder, 'base.pfc')))
    mm.register_scope_providers({
        '*.*': global_repo_provider
    })

    # Here if necessary register object processors or scope providers
    # http://textx.github.io/textX/stable/metamodel/#object-processors
    # http://textx.github.io/textX/stable/scoping/

    return mm
