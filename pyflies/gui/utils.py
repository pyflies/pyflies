from gi.repository import Gtk


def show_error(message):
    dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR,
                               Gtk.ButtonsType.CANCEL, "Error")
    dialog.format_secondary_text(message)
    dialog.run()
    dialog.destroy()
