#!/usr/bin/env python
import os
from gi.repository import Gtk, GtkSource, GObject, Pango

INIT_WIN_WIDTH = 800
INIT_PANED_SPLIT = 800 * 3./4

class PyFliesHandler(object):

    def on_notebook_page_added(self, widget, page_num, user_data):
        """
        When the new tab is created fill it with the 
        source view and tree view.
        """
        page = widget.get_ntx_page(page_num)


class PyFliesApp(object):

    def __init__(self):

        self._init_language_manager()
        self._init_builder()
        self.main_win = self.builder.get_object('pyFliesWindow')
        self.main_win.set_property('default-width', INIT_WIN_WIDTH)

        self.notebook = Gtk.Notebook()
        self.main_win.get_child().get_children()[1].add(self.notebook)

        self.main_win.show_all()
        settings = Gtk.Settings.get_default()
        settings.set_property('gtk-button-images', True)

    def _init_language_manager(self):
        self.language_manager = GtkSource.LanguageManager.new()
        lang_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'lang')

        # Set search path so that our language description is found
        self.language_manager.set_search_path([lang_dir])

    def _init_builder(self):
        self.builder = Gtk.Builder()
        self.glade_file = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'pyflies.glade')

        GObject.type_register(GtkSource.View)
        self.builder.add_from_file(self.glade_file)

        # Connect signal handlers
        self.builder.connect_signals(self)

    def on_new(self, user_data):
        """
        Create new tab content.
        """
        print("On new")
        content = Gtk.Paned(expand=True, orientation=Gtk.Orientation.VERTICAL)
        win_width, _ = self.main_win.get_size()
        paned_split_width = win_width * 3./4
        main_pane = Gtk.Paned(expand=True, position=paned_split_width)
        frame_left = Gtk.Frame(shadow_type=Gtk.ShadowType.IN, expand=True)
        frame_right = Gtk.Frame(shadow_type=Gtk.ShadowType.IN, expand=True)
        content.source_view = self.create_source_view()
        scroll = Gtk.ScrolledWindow(child=content.source_view)
        frame_left.add(scroll)

        # TreeView
        tv_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content.search = Gtk.SearchEntry()
        content.outline = Gtk.TreeView()
        tv_content.add(content.search)
        tv_content.add(content.outline)
        frame_right.add(tv_content)

        main_pane.add1(frame_left)
        main_pane.add2(frame_right)

        # Keep panes proportion on resize
        main_pane.child_set_property(frame_left, 'resize', True)
        main_pane.child_set_property(frame_right, 'resize', True)

        content.add1(main_pane)

        # Graph visualization
        expander = Gtk.Expander(label='Model visualization')
        content.model_graph = Gtk.Image.new_from_file(
                os.path.join(os.path.dirname(__file__),
                '../examples/reference/ref_experiment.dot.png'))
        expander.add(Gtk.ScrolledWindow(child=Gtk.Viewport(child=content.model_graph)))
        content.add2(expander)

        # Notebook page title
        top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        content.file_name = Gtk.Label('Untitled')
        top.add(content.file_name)

        # Page close button
        image = Gtk.Image.new_from_file('./icons/close.png')
        btn_close = Gtk.Button(always_show_image=True, image=image)
        top.add(btn_close)

        content.show_all()
        top.show_all()

        self.notebook.append_page(content, top)
        self.notebook.set_current_page(-1)

    def on_open(self, user_data):
        """
        Loads chosen file in the buffer.
        """
        open_dialog = Gtk.FileChooserDialog(
            title="Pick a file",
            parent=self.main_win,
            modal=True, action=Gtk.FileChooserAction.OPEN,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                     Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT))
        open_dialog.connect("response", self.open_response)
        open_dialog.set_filter(self.filter)
        open_dialog.show()

    def open_response(self, dialog, response_id):

        if response_id == Gtk.ResponseType.ACCEPT:

            file_name = dialog.get_filename()

            # Create new page
            self.on_new(None)

            # Get current notebook page
            page = self.notebook.get_nth_page(self.notebook.get_current_page())

            # Get current buffer
            buffer = page.source_view.get_buffer()

            with open(file_name, 'r') as f:
                buffer.set_text(f.read())

        dialog.destroy()

    def on_save(self, user_data):
        print("Save")
        # file_choser = self.builder.get_object('fcdSave')
        # response = file_choser.run()
        # file_choser.hide()
        #
        # if response == 1:  # Ok
        #     file_name = file_choser.get_filename()
        #     buffer = self.source_view.get_buffer()
        #
        #     with open(file_name, 'w') as f:
        #         f.write(buffer.get_text())


    def on_exit(self, *args):
        Gtk.main_quit(*args)


    def create_source_view(self):
        """
        Creates new source view component
        """
        source_view = GtkSource.View()
        # Set font to monospace
        font = Pango.FontDescription()
        font.set_family('monospace')
        source_view.modify_font(font)

        # Set this source view buffer language to pyflies
        source_view.get_buffer().set_language(
            self.language_manager.get_language('pyflies'))

        return source_view

    @property
    def filter(self):
        filter_text = Gtk.FileFilter()
        filter_text.set_name("PyFlies models")
        filter_text.add_pattern("*.pf")
        return filter_text


def main():
    PyFliesApp()
    return Gtk.main()


if __name__ == "__main__":
    main()
