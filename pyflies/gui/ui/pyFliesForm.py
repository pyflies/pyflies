# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pyflies/gui/ui/pyFliesForm.ui'
#
# Created: Thu Mar 19 22:10:33 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui
from PyQt5.Qt import QWidget, QVBoxLayout, QTabWidget, QStatusBar, QIcon, QPixmap, QToolBar, QAction, QApplication

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)

class Ui_pyFliesWindow(object):
    def setupUi(self, pyFliesWindow):
        pyFliesWindow.setObjectName(_fromUtf8("pyFliesWindow"))
        pyFliesWindow.resize(611, 497)
        self.centralwidget = QWidget(pyFliesWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setMovable(True)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.verticalLayout.addWidget(self.tabWidget)
        pyFliesWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(pyFliesWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        pyFliesWindow.setStatusBar(self.statusbar)
        self.toolBar = QToolBar(pyFliesWindow)
        self.toolBar.setIconSize(QtCore.QSize(32, 32))
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        pyFliesWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionNew = QAction(pyFliesWindow)
        icon = QIcon()
        icon.addPixmap(QPixmap(_fromUtf8(":/icons/icons/new.png")), QIcon.Normal, QIcon.Off)
        self.actionNew.setIcon(icon)
        self.actionNew.setObjectName(_fromUtf8("actionNew"))
        self.actionOpen = QAction(pyFliesWindow)
        icon1 = QIcon()
        icon1.addPixmap(QPixmap(_fromUtf8(":/icons/icons/open.png")), QIcon.Normal, QIcon.Off)
        self.actionOpen.setIcon(icon1)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionSave = QAction(pyFliesWindow)
        icon2 = QIcon()
        icon2.addPixmap(QPixmap(_fromUtf8(":/icons/icons/save.png")), QIcon.Normal, QIcon.Off)
        self.actionSave.setIcon(icon2)
        self.actionSave.setObjectName(_fromUtf8("actionSave"))
        self.actionVisalizationMode = QAction(pyFliesWindow)
        self.actionVisalizationMode.setCheckable(True)
        icon3 = QIcon()
        icon3.addPixmap(QPixmap(_fromUtf8(":/icons/icons/vizmode.png")), QIcon.Normal, QIcon.Off)
        self.actionVisalizationMode.setIcon(icon3)
        self.actionVisalizationMode.setObjectName(_fromUtf8("actionVisalizationMode"))
        self.actionZoomFit = QAction(pyFliesWindow)
        icon4 = QIcon()
        icon4.addPixmap(QPixmap(_fromUtf8(":/icons/icons/zoomfit.png")), QIcon.Normal, QIcon.Off)
        self.actionZoomFit.setIcon(icon4)
        self.actionZoomFit.setObjectName(_fromUtf8("actionZoomFit"))
        self.actionGenerateCode = QAction(pyFliesWindow)
        icon5 = QIcon()
        icon5.addPixmap(QPixmap(_fromUtf8(":/icons/icons/Generate.png")), QIcon.Normal, QIcon.Off)
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
