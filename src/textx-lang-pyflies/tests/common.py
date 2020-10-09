import os
from os.path import join, dirname, abspath
from textx import metamodel_from_file, metamodel_for_language, scoping
import pyflies
from pyflies.lang.common import classes as common_classes, ModelElement
from pyflies.scope import ScopeProvider
from pyflies.lang.pyflies import classes as model_classes
from pyflies.lang.pyflies_processor import processor


this_folder = dirname(abspath(__file__))


class Model(ModelElement, ScopeProvider):
    pass


def get_meta(file_name, classes=None):
    global_repo_provider = scoping.providers.PlainNameGlobalRepo()
    if classes is None:
        classes = model_classes + [Model]
    mm = metamodel_from_file(join(this_folder, file_name), classes=classes,
                             global_repository=True)

    # Load all component models
    component_folder = join(dirname(pyflies.__file__), 'components')
    cmm = metamodel_for_language('pyflies-comp')
    for comp_file in os.listdir(component_folder):
        global_repo_provider.add_model(cmm.model_from_file(join(component_folder, comp_file)))
    mm.register_scope_providers({
        '*.*': global_repo_provider
    })

    mm.register_model_processor(processor)
    return mm

