from PyQt4 import QtGui


def show_error(message):
    QtGui.QMessageBox.critical(None, "PyFlies error", message)


def show_info(title, message):
    QtGui.QMessageBox.information(None, "Information", message)
