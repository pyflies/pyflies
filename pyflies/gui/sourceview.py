import os
from gi.repository import GtkSource, Pango, Gdk
from textx.metamodel import metamodel_from_file
from textx.exceptions import TextXSyntaxError, TextXSemanticError

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

        self.set_highlight_current_line(True)
        self.set_show_line_marks(True)
        self.set_show_line_numbers(True)
        self.set_tab_width(4)
        self.set_auto_indent(True)

        # Error mark attributes
        attr = GtkSource.MarkAttributes(
            icon_name="software-update-urgent",
            background=Gdk.RGBA(230, 40, 40, 1))
        self.set_mark_attributes("error", attr, 1)

        # Set this source view buffer language to pyflies
        self.get_buffer().set_language(
            get_manager().get_language('pyflies'))

    def get_text(self):
        start = self.get_buffer().get_start_iter()
        end = self.get_buffer().get_end_iter()
        return self.get_buffer().get_text(start, end, True)

    def parse(self):
        """
        Parses the content of the buffer, reports error and
        calls outline and graph-view update.
        """
        buf = self.get_buffer()
        start = self.get_buffer().get_start_iter()
        end = self.get_buffer().get_end_iter()
        buf.remove_source_marks(start, end, 'error')
        try:
            self.model = get_metamodel().model_from_str(self.get_text())
        except (TextXSyntaxError, TextXSemanticError) as e:
            if e.line:
                error_mark = buf.create_source_mark(
                    'error', 'error', buf.get_iter_at_line(e.line-1))
                self.scroll_mark_onscreen(error_mark)
            return (str(e), e.line, e.col)


