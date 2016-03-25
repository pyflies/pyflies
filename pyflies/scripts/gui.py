import sys
from PyQt4 import QtGui
from pyflies.gui import PyFliesWindow


def pyfliesgui():
    """
    Entry point to run GUI.
    """

    app = QtGui.QApplication(sys.argv)

    w = PyFliesWindow()
    w.show()

    sys.exit(app.exec_())
