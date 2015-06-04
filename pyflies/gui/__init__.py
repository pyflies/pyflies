#!/usr/bin/env python
import os
import sys
import uuid
from subprocess import call
from PyQt4 import QtGui, QtCore
from textx.exceptions import TextXError
from textx.export import model_export

# from gi.repository import Gtk, GtkSource, GObject

from pyflies.lang.pflang import pyflies_mm
from .ui.pyFliesForm import Ui_pyFliesWindow
from .modelviewer import ModelGraphView, ModelGraphScene
from .codeeditor import CodeEditor
from pyflies.export import custom_export
from pyflies.exceptions import PyFliesException
from pyflies.gui.utils import show_error, show_info
from pyflies.generators import generator_names, generate

INIT_WIN_WIDTH = 800
INIT_PANED_SPLIT = 800 * 3./4
UNTITLED = "Untitled"


class PyFliesWindow(QtGui.QMainWindow, Ui_pyFliesWindow):
    def __init__(self):
        super(PyFliesWindow, self).__init__()
        self.setupUi(self)
        self.resize(1000, 600)
        self.update_action_states()

    @property
    def current_editor(self):
        """
        Returns a textual editor component of the current tab.
        """
        return self.tabWidget.currentWidget().widget(0)

    @property
    def current_graphview(self):
        """
        Returns a graph view widget of the current tab.
        """
        return self.tabWidget.currentWidget().widget(1)

    @property
    def current_tab(self):
        """
        Returns current tab widget (in this case QSplitter).
        """
        return self.tabWidget.currentWidget()

    def update_action_states(self):
        """
        Enable/disable actions.
        """
        enabled = self.tabWidget.count() > 0
        self.actionSave.setEnabled(enabled)
        self.actionVisalizationMode.setEnabled(enabled)
        self.actionZoomFit.setEnabled(enabled)
        self.actionGenerateCode.setEnabled(enabled)

    def new_tab(self, filename):
        # Create new scene and view
        scene = ModelGraphScene()
        view = ModelGraphView(scene)

        splitter = QtGui.QSplitter()

        # Create code editor
        editor = CodeEditor()
        editor.setTabStopWidth(40)

        splitter.addWidget(editor)
        splitter.addWidget(view)

        splitter.setSizes([200, 150])

        self.tabWidget.addTab(splitter, os.path.basename(filename))
        self.tabWidget.setCurrentWidget(splitter)

        editor.filename = filename

        # Dirty flag support
        editor.dirty = False
        editor.open = False

        self.update_action_states()

        def on_text_changed():
            """
            Sets dirty flag on document contents change.
            """
            editor.dirty = True

            # On first change during open we do not want to update title.
            if editor.open:
                editor.open = False
                return

            # Find index of root splitter widget for this editor
            editor_tab_index = self.tabWidget.indexOf(editor.parent())

            if editor_tab_index >= 0:
                tab_text = self.tabWidget.tabText(editor_tab_index)
                if not tab_text.endswith('*'):
                    self.tabWidget.setTabText(editor_tab_index,
                                              '%s*' % tab_text)

        editor.textChanged.connect(on_text_changed)

    def save_current(self, filename=None):
        """
        Save file at current tab.
        """

        if not filename:
            filename = self.current_editor.filename

        with open(filename, 'w') as f:
            f.write(self.current_editor.toPlainText())

        self.tabWidget.setTabText(self.tabWidget.currentIndex(),
                                  os.path.basename(filename))
        self.current_editor.filename = filename

        self.update_model()

    def update_model(self):
        """
        Parses code, updates model. If error is raised, highlight line and
        update statusbar.
        """
        try:
            model = pyflies_mm.model_from_str(
                str(self.current_editor.toPlainText()))
            model._filename = self.current_editor.filename
            self.current_editor.model = model

            dot_file = str(uuid.uuid4())
            if self.actionVisalizationMode.isChecked():
                model_export(model, dot_file)
            else:
                custom_export(model, dot_file)

            svg_file = "%s.jpg" % dot_file
            call(["dot", "-Tjpg", "-O", dot_file])
            self.current_graphview.scene().load_svg(svg_file)
            os.remove(svg_file)
            os.remove(dot_file)
            self.statusbar.clearMessage()

        except TextXError as e:
            self.current_editor.highlight_error(e.line, e.col)
            self.statusbar.showMessage(str(e))

    @QtCore.pyqtSlot()
    def on_actionNew_triggered(self):
        self.new_tab(UNTITLED)

    @QtCore.pyqtSlot()
    def on_actionOpen_triggered(self):
        filename = str(QtGui.QFileDialog.getOpenFileName(
            self, 'Open Experiment', '', 'pyFlies experiments (*.pf)'))

        # Parse input
        if filename:
            self.new_tab(filename)
            self.current_editor.open = True
            self.current_editor.setPlainText(open(filename).read())
            self.update_model()
            self.current_graphview.fit_in_view()

    @QtCore.pyqtSlot()
    def on_actionSave_triggered(self):

        if self.current_editor.filename == UNTITLED:
            filename = QtGui.QFileDialog.getSaveFileName(
                self, 'Save Experiment', '', 'pyFlies experiments (*.pf)')

            if not filename:
                return

        else:
            filename = self.current_editor.filename

        self.save_current(filename)

    @QtCore.pyqtSlot()
    def on_actionVisalizationMode_triggered(self):
        self.update_model()
        self.current_graphview.fit_in_view()

    @QtCore.pyqtSlot()
    def on_actionZoomFit_triggered(self):
        self.current_graphview.fit_in_view()

    @QtCore.pyqtSlot()
    def on_actionGenerateCode_triggered(self):
        gen_names = generator_names()

        if not hasattr(self.current_editor, 'model'):
            show_error("There is no model in the editor."
                       "Type in experiment model and save it before running"
                       " code generation.")
            return

        model = self.current_editor.model
        targets = model.targets

        if len(targets) == 0:
            show_error(("No targets specified.\n" +
                        "Define one or more target specification at " +
                        "the end of the file.\n" +
                        "Installed targets are: {} \n")
                       .format(", ".join(gen_names)))
            return

        # Check if there is generator for each target
        for target in targets:
            if target.name not in gen_names:
                line, _ = \
                    model.metamodel.parser.pos_to_linecol(target._position)
                show_error("Unexisting target '{}' at line {}."
                           .format(target.name, line))

        for target in targets:
            # Call generator
            try:
                generate(model, target)
            except PyFliesException as e:
                show_error(str(e))
                return

        show_info("Code generation",
                  "Code for target platform(s) generated sucessfully.")

    @QtCore.pyqtSlot(int)
    def on_tabWidget_tabCloseRequested(self, index):
        print("Close", index)
        self.tabWidget.removeTab(index)
        self.update_action_states()


def main():
    app = QtGui.QApplication(sys.argv)

    w = PyFliesWindow()
    w.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
