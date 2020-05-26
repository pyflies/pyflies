import sys
from PyQt5.Qt import QApplication
from pyflies.gui import PyFliesWindow


def pyfliesgui():
    """
    Entry point to run GUI.
    """

    app = QApplication(sys.argv)

    w = PyFliesWindow()
    w.show()

    sys.exit(app.exec_())
