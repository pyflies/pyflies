from textx.metamodel import metamodel_from_file
from textx.export import metamodel_export

pyflies_mm = metamodel_from_file('pyflies.tx')
metamodel_export(pyflies_mm, 'pyflies_meta.dot')
