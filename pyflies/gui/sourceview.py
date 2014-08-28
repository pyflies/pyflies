import os
from gi.repository import GtkSource, Pango
from textx.metamodel import metamodel_from_file
from textx.exceptions import TextXSyntaxError

_language_manager = None
_metamodel = None


def get_manager():
    """
    Initialize and returns language manager.
    """
    global _language_manager

    if not _language_manager:
        _language_manager = GtkSource.LanguageManager.new()
        lang_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', 'lang')

        # Set search path so that our language description is found
        _language_manager.set_search_path([lang_dir])

    return _language_manager


def get_metamodel():
    """
    Initialize and return pyFlies metamodel.
    """
    global _metamodel

    if not _metamodel:
        _metamodel = metamodel_from_file(
            os.path.join(os.path.dirname(__file__),
                         '..', 'lang', 'pyflies.tx'),
            builtins={'categorisation': 'categorisation',
                      'visual': 'visual'})
    return _metamodel


class PyFliesSourceView(GtkSource.View):
    def __init__(self):
        super(PyFliesSourceView, self).__init__()
        # Set font to monospace
        font = Pango.FontDescription()
        font.set_family('monospace')
        self.modify_font(font)

        # Set this source view buffer language to pyflies
        self.get_buffer().set_language(
            get_manager().get_language('pyflies'))

    def parse(self):
        """
        Parses the content of the buffer, reports error and
        calls outline and graph-view update.
        """
        start, end = self.get_buffer().get_bounds()
        try:
            self.model = get_metamodel().model_from_str(
                self.get_buffer().get_text(start, end, True))
        except TextXSyntaxError as e:
            pass

