from gi.repository import Gtk


def show_error(message):
    dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR,
                               Gtk.ButtonsType.OK, "Error")
    dialog.format_secondary_text(message)
    dialog.run()
    dialog.destroy()


def show_info(title, message):
    dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.INFO,
                               Gtk.ButtonsType.OK, title)
    dialog.format_secondary_text(message)
    dialog.run()
    dialog.destroy()
