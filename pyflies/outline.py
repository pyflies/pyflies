import os
from gi.repository import Gtk


class Outline(Gtk.VBox):
    """
    Tree outline with search
    """
    def __init__(self):
        super(Outline, self).__init__()
        self.builder = Gtk.Builder()
        self.glade_file = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'outline.glade')

        self.builder.add_from_file(self.glade_file)
        self.add(self.builder.get_object('outline'))

