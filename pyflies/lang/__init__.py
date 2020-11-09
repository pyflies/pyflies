import os
from os.path import join, dirname
from textx import language, metamodel_from_file, metamodel_for_language, scoping
import pyflies
from .pyflies_processor import processor
from .pyflies import classes as pyflies_classes
from .components import classes as component_classes
from .common import reduce_exp


current_dir = dirname(__file__)


@language('pyflies', '*.pf')
def pyflies_language():
    "A language for psychology experiments specification"

    builtin_models = scoping.ModelRepository()
    cmm = metamodel_for_language('pyflies-comp')
    component_folder = join(dirname(pyflies.__file__), '..', 'components')

    for comp_file in os.listdir(component_folder):
        cm = cmm.model_from_file(join(component_folder, comp_file))
        reduce_exp(cm)
        builtin_models.add_model(cm)

    mm = metamodel_from_file(join(current_dir, 'pyflies.tx'),
                             autokwd=True,
                             classes=pyflies_classes, builtin_models=builtin_models)

    mm.model_param_defs.add(
        "group", "A group identifier used in counterbalancing"
    )

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
    m = mm.model_from_file(join(component_folder, 'base.pfc'))
    reduce_exp(m)
    global_repo_provider.add_model(m)
    mm.register_scope_providers({
        '*.*': global_repo_provider
    })

    # Here if necessary register object processors or scope providers
    # http://textx.github.io/textX/stable/metamodel/#object-processors
    # http://textx.github.io/textX/stable/scoping/

    return mm
