from itertools import ifilter

HEADER = '''
digraph pyflies {
  rankdir=LR;
  node[
      shape=record,
      style=filled,
      fillcolor=aliceblue
  ]

  start [shape=circle, fillcolor=black, width=0.2, height=0.2, label="", fixedsize=true];
  end [shape=doublecircle, fillcolor=black, width=0.2, height=0.2, label="", fixedsize=true];

'''


def custom_export(model, file_name):

    with open(file_name, 'w') as f:
        f.write(HEADER)

        # Find experiment
        experiment = next(ifilter(
            lambda x: x.__class__.__name__ == "Experiment",
            model.elements), None)

        last_node = 'start'

        if experiment:
            for e in experiment.elements:
                clsname = e.__class__.__name__
                if clsname == "TextReference":
                    node_name = e.text.name
                    f.write('{} [shape=note, fillcolor=green, label="{}"];'
                            .format(e.text.name, e.text.content))
                elif clsname == "SubjectReference":
                    node_name = e.subject.name
                    attr_str = ""
                    for attr in e.subject.attribute:
                        if attr.type.__class__.__name__ == "Enum":
                            attr_type = "[{}]".format(
                                ", ".join(attr.type.values))
                        else:
                            attr_type = attr.type
                        attr_str += "{}:{}\\l".format(attr.name, attr_type)

                    f.write('{} [shape=record, label="{{Subject|{}}}"];'
                            .format(node_name, attr_str))
                elif clsname == "TestReference":
                    node_name = e.test.name
                    color = "green" if e.test.practice else "red"
                    randomize = "randomize" if e.test.randomize else ""
                    f.write(''' {} [shape=doubleoctagon,fillcolor={}, label=<
<FONT POINT-SIZE="20">{}</FONT><BR/>
<FONT POINT-SIZE="15">tmin:{}</FONT><BR/>
<FONT POINT-SIZE="15">tmax:{}</FONT><BR/>
<FONT POINT-SIZE="15">twait:{}</FONT><BR/>
                            {}
                            >]'''.format(
                            node_name, color, e.test.name, e.test.tmin,
                            e.test.tmax, e.test.twait, randomize))
                elif clsname == "Sequence":
                    pass
                elif clsname == "Randomize":
                    pass

                f.write('{} -> {};'.format(last_node, node_name))
                last_node = node_name

        f.write("{} -> end;".format(last_node))
        f.write('\n}\n')

