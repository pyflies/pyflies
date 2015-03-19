# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pyflies/gui/ui/pyFliesForm.ui'
#
# Created: Thu Mar 19 22:10:33 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_pyFliesWindow(object):
    def setupUi(self, pyFliesWindow):
        pyFliesWindow.setObjectName(_fromUtf8("pyFliesWindow"))
        pyFliesWindow.resize(611, 497)
        self.centralwidget = QtGui.QWidget(pyFliesWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setMovable(True)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.verticalLayout.addWidget(self.tabWidget)
        pyFliesWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(pyFliesWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        pyFliesWindow.setStatusBar(self.statusbar)
        self.toolBar = QtGui.QToolBar(pyFliesWindow)
        self.toolBar.setIconSize(QtCore.QSize(32, 32))
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        pyFliesWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionNew = QtGui.QAction(pyFliesWindow)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/new.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionNew.setIcon(icon)
        self.actionNew.setObjectName(_fromUtf8("actionNew"))
        self.actionOpen = QtGui.QAction(pyFliesWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/open.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionOpen.setIcon(icon1)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionSave = QtGui.QAction(pyFliesWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/save.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSave.setIcon(icon2)
        self.actionSave.setObjectName(_fromUtf8("actionSave"))
        self.actionVisalizationMode = QtGui.QAction(pyFliesWindow)
        self.actionVisalizationMode.setCheckable(True)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/vizmode.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionVisalizationMode.setIcon(icon3)
        self.actionVisalizationMode.setObjectName(_fromUtf8("actionVisalizationMode"))
        self.actionZoomFit = QtGui.QAction(pyFliesWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/zoomfit.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionZoomFit.setIcon(icon4)
        self.actionZoomFit.setObjectName(_fromUtf8("actionZoomFit"))
        self.actionGenerateCode = QtGui.QAction(pyFliesWindow)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/Generate.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionGenerateCode.setIcon(icon5)
        self.actionGenerateCode.setObjectName(_fromUtf8("actionGenerateCode"))
        self.toolBar.addAction(self.actionNew)
        self.toolBar.addAction(self.actionOpen)
        self.toolBar.addAction(self.actionSave)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionVisalizationMode)
        self.toolBar.addAction(self.actionZoomFit)
        self.toolBar.addAction(self.actionGenerateCode)

        self.retranslateUi(pyFliesWindow)
        self.tabWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(pyFliesWindow)

    def retranslateUi(self, pyFliesWindow):
        pyFliesWindow.setWindowTitle(_translate("pyFliesWindow", "pyFlies", None))
        self.toolBar.setWindowTitle(_translate("pyFliesWindow", "toolBar", None))
        self.actionNew.setText(_translate("pyFliesWindow", "New", None))
        self.actionNew.setToolTip(_translate("pyFliesWindow", "New experiment model", None))
        self.actionNew.setShortcut(_translate("pyFliesWindow", "Ctrl+N", None))
        self.actionOpen.setText(_translate("pyFliesWindow", "Open", None))
        self.actionOpen.setToolTip(_translate("pyFliesWindow", "Open experiment", None))
        self.actionOpen.setShortcut(_translate("pyFliesWindow", "Ctrl+O", None))
        self.actionSave.setText(_translate("pyFliesWindow", "Save", None))
        self.actionSave.setToolTip(_translate("pyFliesWindow", "Save experiment", None))
        self.actionSave.setShortcut(_translate("pyFliesWindow", "Ctrl+S", None))
        self.actionVisalizationMode.setText(_translate("pyFliesWindow", "Visalization mode", None))
        self.actionVisalizationMode.setToolTip(_translate("pyFliesWindow", "Change visualization mode", None))
        self.actionZoomFit.setText(_translate("pyFliesWindow", "Zoom to fit", None))
        self.actionZoomFit.setToolTip(_translate("pyFliesWindow", "Zoom to fit", None))
        self.actionGenerateCode.setText(_translate("pyFliesWindow", "Generate code", None))
        self.actionGenerateCode.setToolTip(_translate("pyFliesWindow", "Generate experiment code", None))

from . import resources_rc
