"""
A script to generate component documentation from component description.

See ../pyflies/components/ folder
"""
import jinja2
import pyflies
import glob
import datetime
from os.path import basename, splitext, dirname, abspath, join

sort_order = ['abstract component', 'extends visual', 'extends audible', 'extends input']

this_folder = dirname(abspath(__file__))
template_file = join(this_folder, 'components.md.jinja')
component_docs_file = join(this_folder, '..', 'docs', 'components.md')
components_path = join(dirname(abspath(pyflies.__file__)), 'components', '*.pfc')

component_files = [f for f in glob.glob(components_path)]

component_files.sort(key=lambda x: 0 if 'base' in x else 1)

components = []
for c in component_files:
    cname = splitext(basename(c))[0]
    with open(c, 'r') as f:
        content = f.read()

    components.append({
        'name': cname,
        'content': content
    })

components.sort(key=lambda x: [idx if o in x['content'] else 10
                               for idx, o in enumerate(sort_order)])

now = datetime.datetime.now()
now = now.strftime('%Y-%m-%d %H:%M:%S')

with open(template_file, 'r') as t:
    tcontent = t.read()
    with open(component_docs_file, 'w') as cf:
        cf.write(jinja2.Template(tcontent).render(components=components, now=now))
