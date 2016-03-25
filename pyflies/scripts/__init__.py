import sys
import argparse
from PyQt4 import QtGui
from pyflies.gui import PyFliesWindow
from pyflies.lang.pflang import pyflies_mm
from pyflies.generators import generator_names, generate
from pyflies.exceptions import PyFliesException


def pyfliesgui():
    """
    Entry point to run GUI.
    """

    app = QtGui.QApplication(sys.argv)

    w = PyFliesWindow()
    w.show()

    sys.exit(app.exec_())


def pyflies():
    """
    Entry point to run code generator from command line.
    """

    class MyParser(argparse.ArgumentParser):
        """
        Custom arugment parser for printing help message in case of error.
        See http://stackoverflow.com/questions/4042452/display-help-message-with-python-argparse-when-script-is-called-without-any-argu
        """
        def error(self, message):
            sys.stderr.write('error: %s\n' % message)
            self.print_help()
            sys.exit(2)

    parser = MyParser(description="pyflies model translator.")
    parser.add_argument('model', help="Model file name")

    args = parser.parse_args()

    try:
        model = pyflies_mm.model_from_file(args.model)
    except Exception as e:
        print(e)
        return

    gen_names = generator_names()
    if not model.targets:
        print("No targets specified.\n"
              "Define one or more target specification at "
              "the end of the file.\n"
              "Installed targets are: {} \n"
              .format(", ".join(gen_names)))
        return

    # Check if there is generator for each target
    for target in model.targets:
        if target.name not in gen_names:
            line, _ = \
                model.metamodel.parser.pos_to_linecol(target._position)
            print("Unexisting target '{}' at line {}."
                        .format(target.name, line))

    for target in model.targets:
        # Call generator
        print("Generating code for target {}(out={})..."\
              .format(target.name, target.output), end="")
        try:
            generate(model, target)
        except Exception as e:
            print(str(e))
            return
        finally:
            print("Done")

    print("Code for target platform(s) generated sucessfully.")
