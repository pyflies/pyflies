#!/usr/bin/env python
import os
from gi.repository import Gtk, GtkSource, GObject

from .modelviewer import ModelGraphViewer
from .outline import Outline
from .sourceview import PyFliesSourceView

INIT_WIN_WIDTH = 800
INIT_PANED_SPLIT = 800 * 3./4


class PyFliesGUI(object):

    def __init__(self):

        self._init_builder()
        self.main_win = self.builder.get_object('pyFliesWindow')
        self.main_win.set_property('default-width', INIT_WIN_WIDTH)

        self.notebook = Gtk.Notebook()
        self.main_win.get_child().get_children()[1].add(self.notebook)

        self.main_win.show_all()
        settings = Gtk.Settings.get_default()
        settings.set_property('gtk-button-images', True)

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
        Create new page for Notebook.
        """
        win_width, win_height = self.main_win.get_size()
        # Page will contain the content paned and status bar
        page = Gtk.VBox(homogeneous=False)

        content = Gtk.Paned(expand=True, position=win_height * 1./2,
                            orientation=Gtk.Orientation.VERTICAL)

        # Each page has its own statusbar
        page.add(content)
        page.status_bar = Gtk.Statusbar()
        page.add(page.status_bar)
        page.child_set_property(content, "expand", True)
        page.child_set_property(page.status_bar, "expand", False)

        paned_split_width = win_width * 3./4
        main_pane = Gtk.Paned(expand=True, position=paned_split_width)
        frame_left = Gtk.Frame(shadow_type=Gtk.ShadowType.IN, expand=True)
        frame_right = Gtk.Frame(shadow_type=Gtk.ShadowType.IN, expand=True)
        page.source_view = PyFliesSourceView()
        scroll = Gtk.ScrolledWindow(child=page.source_view)
        frame_left.add(scroll)

        # TreeView outline
        frame_right.add(Outline())

        main_pane.add1(frame_left)
        main_pane.add2(frame_right)

        # Keep panes proportion on resize
        main_pane.child_set_property(frame_left, 'resize', True)
        main_pane.child_set_property(frame_right, 'resize', True)

        content.add1(main_pane)

        # Graph visualization
        model_viewer_frame = Gtk.Frame(label='Model visualization')
        page.model_viewer = ModelGraphViewer()
        model_viewer_frame.add(page.model_viewer)
        content.add2(model_viewer_frame)

        # Notebook page title
        top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        page.file_name = Gtk.Label('Untitled')
        top.add(page.file_name)

        # Page close button
        image = Gtk.Image.new_from_file('./icons/close.png')
        btn_close = Gtk.Button(always_show_image=True, image=image)
        top.add(btn_close)

        page.show_all()
        top.show_all()

        self.notebook.append_page(page, top)
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

            with open(file_name, 'r') as f:
                self.current_page.source_view.get_buffer().set_text(f.read())

        dialog.destroy()
        self.update_model()

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

    def update_model(self, ):
        error = self.current_page.source_view.parse()
        if error:
            sbar = self.current_page.status_bar
            context_id = sbar.get_context_id('error')
            sbar.remove_all(context_id)
            sbar.push(context_id, "Error: {}".format(error[0]))
        else:
            # Update model viewer
            self.current_page.model_viewer.update_model(
                self.current_page.source_view.model)

    @property
    def current_page(self):
        # Get current notebook page
        return self.notebook.get_nth_page(self.notebook.get_current_page())

    @property
    def filter(self):
        filter_text = Gtk.FileFilter()
        filter_text.set_name("PyFlies models")
        filter_text.add_pattern("*.pf")
        return filter_text


def main():
    PyFliesGUI()
    return Gtk.main()


if __name__ == "__main__":
    main()
