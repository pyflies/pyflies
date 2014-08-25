#!/usr/bin/env python
import os
from gi.repository import Gtk, GtkSource, GObject, Pango


class PyFliesHandler(object):

    def __init__(self, builder):
        self.builder = builder
        self.source_view = builder.get_object('gtksourceview')

        font = Pango.FontDescription()
        font.set_family('monospace')
        self.source_view.modify_font(font)

        manager = GtkSource.LanguageManager.new()
        lang_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'lang')
        manager.set_search_path([lang_dir])
        print(manager.get_language_ids())
        self.source_view.get_buffer().set_language(
            manager.get_language('pyflies'))

    def OnExit(self, *args):
        Gtk.main_quit(*args)

    def OnOpen(self, user_data):
        file_choser = self.builder.get_object('filechooserdialog')
        response = file_choser.run()
        file_choser.hide()

        if response == 1:  # Ok
            file_name = file_choser.get_filename()
            buffer = self.source_view.get_buffer()

            with open(file_name, 'r') as f:
                buffer.set_text(f.read())


class PyFliesApp(object):

    def __init__(self):
        self.builder = Gtk.Builder()
        self.glade_file = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'pyflies.glade')

        GObject.type_register(GtkSource.View)
        self.builder.add_from_file(self.glade_file)

        # Connect signal handlers
        handler = PyFliesHandler(self.builder)
        self.builder.connect_signals(handler)

        main_win = self.builder.get_object('pyFliesWindow')
        main_win.show_all()


def main():
    PyFliesApp()
    return Gtk.main()


if __name__ == "__main__":
    main()
