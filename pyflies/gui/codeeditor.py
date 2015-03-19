from PyQt4 import QtGui

from textx.metamodel import metamodel_from_file

class CodeEditor(QtGui.QPlainTextEdit):

    def update_all(self):
        """
        Parses contained text and updates model, return any
        error and updates the line highlighting.

        Returs:
            (error, line): In case of an error.
        """
        try:
            self.model = metamodel.model_from_str(self.plainText)
        except TextXError as e:
            self.highlight_error(e.line)
            return e.message, e.line


    def highlight_error(self, line):
        # TODO: Line highlight
        pass

metamodel = metamodel_from_file(
    os.path.join(os.path.dirname(__file__), '..', 'lang', 'pyflies.tx')

