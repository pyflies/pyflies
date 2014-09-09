#!/usr/bin/env python
import os
from gi.repository import Gtk, GtkSource, GObject

from .modelviewer import ModelGraphViewer
from .outline import Outline
from .sourceview import PyFliesSourceView
from pyflies.exceptions import PyFliesException
from pyflies.gui.utils import show_error, show_info
from pyflies.generators import generator_names, generate

INIT_WIN_WIDTH = 800
INIT_PANED_SPLIT = 800 * 3./4
UNTITLED = "Untitled"


class PyFliesGUI(object):

    def __init__(self):

        self._init_builder()
        self.main_win = self.builder.get_object('pyFliesWindow')
        self.main_win.set_property('default-width', INIT_WIN_WIDTH)

        # Action group for page
        self.actiongroupPage = self.builder.get_object("actiongroupPage")
        # Disable actions
        self.actiongroupPage.set_sensitive(False)

        # Visualization type
        self.vistype_button = self.builder.get_object("tbVisType")
        self.id_on_vistype_toggle = self.vistype_button.connect(
            "toggled", self.on_vistype_toggle)

        # Code generation
        self.generate_dialog = self.builder.get_object("generateDialog")
        self.generate_dialog.connect("response", self.generate_response)
        self.targets_combo = self.builder.get_object("cmbTargets")
        for gen_name in generator_names():
            self.targets_combo.append_text(gen_name)
        self.target_folder_combo = self.builder.get_object("fcOutput")

        self.notebook = Gtk.Notebook()
        self.main_win.get_child().get_children()[1].add(self.notebook)
        self.notebook.connect("switch-page", self.on_page_change)

        self.main_win.show_all()
        settings = Gtk.Settings.get_default()
        settings.set_property('gtk-button-images', True)

    def _init_builder(self):
        self.builder = Gtk.Builder()
        main_glade_file = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'pyflies.glade')
        generate_glade_file = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'generate.glade')

        GObject.type_register(GtkSource.View)
        self.builder.add_from_file(main_glade_file)
        self.builder.add_from_file(generate_glade_file)

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
        page.file_name_label = Gtk.Label(UNTITLED)
        top.add(page.file_name_label)
        page.file_name = UNTITLED

        # Page close button

        self.glade_file = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'pyflies.glade')
        image = Gtk.Image.new_from_file(os.path.join(
                                        os.path.dirname(__file__),
                                        'icons', 'close.png'))
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

            # Update file_name
            self.update_filename(file_name)

            self.update_model()

        dialog.destroy()

    def on_save(self, user_data):
        print("Save")
        # If file is Untitled bring on a save dialog
        # If the name is different save the file and
        # run model update.
        file_name = self.current_page.file_name
        if file_name == UNTITLED:
            save_dialog = Gtk.FileChooserDialog(
                title="Enter a file name",
                parent=self.main_win,
                modal=True, action=Gtk.FileChooserAction.SAVE,
                buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                         Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT))
            save_dialog.connect("response", self.save_response)
            save_dialog.set_filter(self.filter)
            save_dialog.show()

        else:
            self.save_current()

    def save_response(self, dialog, response_id):

        if response_id == Gtk.ResponseType.ACCEPT:
            self.update_filename(dialog.get_filename())
            self.save_current()

        dialog.destroy()

    def save_current(self):
        file_name = self.current_page.file_name
        with open(file_name, 'w') as f:
            f.write(self.current_page.source_view.get_text())
        self.update_model()

    def on_page_change(self, notebook, page, user_data):
        # Enable actions if there is model
        self.actiongroupPage.set_sensitive(page.source_view.model is not None)

        # Update visualization type button state without triggering
        # toggle handler
        self.vistype_button.handler_block(self.id_on_vistype_toggle)
        self.vistype_button.set_active(page.model_viewer.get_vis_type())
        self.vistype_button.handler_unblock(self.id_on_vistype_toggle)

    def on_vistype_toggle(self, button):
        active = button.get_active()
        self.current_page.model_viewer.set_vis_type(active)
        self.current_page.model_viewer.best_fit()

    def on_bestfit(self, button):
        self.current_page.model_viewer.best_fit()

    def on_generate(self, button):
        print("Generate")

        gen_names = generator_names()

        model = self.current_model
        targets = model.targets

        if len(targets) == 0:
            show_error("No targets specified.\n" +
                       "Define one or more target specification at " +
                       "the end of file.\n" +
                       "Installed targets are: {}"
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
            output = target.output

            # Extract response map
            responses = {}
            for r in target.responseMap:
                responses[r.name] = r.target

            # Extract param values map
            params = {}
            for p in target.targetParam:
                params[p.name] = p.value

            # Call generator
            try:
                generate(target.name, output, model, responses, params)
            except PyFliesException as e:
                show_error(str(e))
                return

        show_info("Code generation", "Code for target platform(s) generated sucessfully.")

    def on_exit(self, *args):
        Gtk.main_quit(*args)

    def update_model(self):
        # Clear status bar
        sbar = self.current_page.status_bar
        context_id = sbar.get_context_id('error')
        sbar.remove_all(context_id)

        error = self.current_page.source_view.parse()
        if error:
            message = error[0].replace('\n', ' ').replace('\r', '')
            sbar.push(context_id, "Error: {}".format(message))
        else:
            # Update model viewer
            self.current_page.model_viewer.update_model(
                self.current_page.source_view.model)
            # TODO: Update outline view

        # Update buttons
        self.actiongroupPage.set_sensitive(self.current_model is not None)

    def update_filename(self, file_name):
        self.current_page.file_name = file_name
        _, file_part = os.path.split(file_name)
        self.current_page.file_name_label.set_text(file_part)

    @property
    def current_page(self):
        # Get current notebook page
        return self.notebook.get_nth_page(self.notebook.get_current_page())

    @property
    def current_model(self):
        cp = self.current_page
        if cp:
            return cp.source_view.model

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
