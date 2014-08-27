from textx.metamodel import metamodel_from_file
from textx.export import metamodel_export, model_export

pyflies_mm = metamodel_from_file('../../pyflies/lang/pyflies.tx')
metamodel_export(pyflies_mm, 'pyflies_meta.dot')

experiment = pyflies_mm.model_from_file('ref_experiment.pf')
model_export(experiment, 'ref_experiment.dot')

