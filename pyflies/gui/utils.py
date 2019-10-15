from PyQt5 import QtGui
from PyQt5.Qt import QMessageBox

def show_error(message):
    QMessageBox.critical(None, "PyFlies error", message)


def show_info(title, message):
    QMessageBox.information(None, "Information", message)
