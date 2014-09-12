HEADER = '''
digraph pyflies {
  rankdir=TD;
  node[
      shape=record,
      style=filled,
      fillcolor=aliceblue
  ]

  start [shape=circle, fillcolor=black, width=0.2, height=0.2, label="", fixedsize=true];
  end [shape=doublecircle, fillcolor=black, width=0.2, height=0.2, label="", fixedsize=true];

'''

# Cluster for sequence and randomize blocks
cluster = 1
last_node = 'start'
node_num = 1


def custom_export(model, file_name):

    global cluster, last_node, node_num

    # Cluster for sequence and randomize blocks
    cluster = 1
    node_num = 1
    last_node = 'start'

    # Find structure
    structure = model.structure

    if structure:

        def _render_dot(e):
            """
            Renders experiment element.
            """

            global cluster, last_node, node_num

            clsname = e._typename

            if clsname == "ScreenInstance":
                f.write('{} [shape=note, fillcolor=lawngreen, label="{}"];\n'
                        .format(node_num, e.type.content))
                node_num += 1
            elif clsname == "SubjectInstance":
                attr_str = ""
                for attr in e.type.attribute:
                    if attr.type.__class__.__name__ == "Enum":
                        attr_type = "[{}]".format(
                            ", ".join(attr.type.values))
                    else:
                        attr_type = attr.type
                    attr_str += "{}:{}\\l".format(attr.name, attr_type)

                f.write('{} [shape=record, label="{{Subject|{}}}"];\n'
                        .format(node_num, attr_str))
                node_num += 1
            elif clsname == "TestInstance":
                color = "lawngreen" if e.practice else "red"
                randomize = '<FONT POINT-SIZE="15">randomize</FONT><BR/>'\
                    if e.randomize else ""

                f.write(''' {} [shape=doubleoctagon,fillcolor={}, label=<
<FONT POINT-SIZE="20">{}</FONT><BR/>
<FONT POINT-SIZE="15">conditions: {}</FONT><BR/>
<FONT POINT-SIZE="15">variables: {}</FONT><BR/>
<FONT POINT-SIZE="15">tmin: {}</FONT><BR/>
<FONT POINT-SIZE="15">tmax: {}</FONT><BR/>
{}
                        >];\n'''.format(
                        node_num, color, e.type.name,
                        len(e.type.conditions.conditions),
                        ", ".join(e.type.condvar_map.keys()), e.type.tmin,
                        e.type.tmax, randomize))
                f.write('{} -> {} [dir=back, label="{}"];\n'.format(
                    node_num, node_num, e.trials*len(e.type.conditions.conditions)))
                node_num += 1
            elif clsname == "Sequence":
                f.write('''subgraph cluster{} {{
                            label="";
                            style=dotted;
                            penwidth=2;
                            color=black;\n\n'''.format(cluster))
                cluster += 1
                for x in e.elements:
                    _render_dot(x)
                f.write('}\n')
            elif clsname == "Randomize":
                f.write('''subgraph cluster{} {{
                            style=solid;
                            color=yellow;
                            penwidth=2;
                            label = "randomize";\n\n'''.format(cluster))
                cluster += 1
                for x in e.elements:
                    _render_dot(x)
                f.write('}\n')

        with open(file_name, 'w') as f:
            f.write(HEADER)

            for elem in structure.elements:
                _render_dot(elem)

            # Connections
            if node_num > 1:
                f.write('start -> 1;\n')
                n = 0
                for n in range(1, node_num-1):
                    f.write('{} -> {};\n'.format(n, n+1))

                f.write("{} -> end;\n".format(n+1))
            else:
                f.write("start -> end;\n")
            f.write('\n}\n')

