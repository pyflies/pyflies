import os
import uuid
from PyQt4 import QtGui, QtSvg
from PyQt4.Qt import Qt
from subprocess import call

from textx.export import model_export
from pyflies.export import custom_export


class ModelGraphScene(QtGui.QGraphicsScene):

    def load_svg(self, svg_file):
        # item = QtSvg.QGraphicsSvgItem(svg_file)
        self.clear()
        item = QtGui.QPixmap(svg_file)
        self.addPixmap(item)


class ModelGraphView(QtGui.QGraphicsView):
    """
    View widget for the experiment model.
    """
    ZOOM_IN_SCALE = 1.2589254

    def __init__(self, scene):
        super(ModelGraphView, self).__init__(scene)

        # SceneView has capability to track mouse events, enable it
        self.setMouseTracking(True)

        # Anchor under mouse
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)

        # Seting hints which enable antialiasing
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setRenderHint(QtGui.QPainter.TextAntialiasing)

    def wheelEvent(self, wheel_event):
        """
        Event handler for mouse wheel event over view enabling
        point zoom feature.
        """
        delta = wheel_event.delta()

        if delta > 0:
            self.scale(self.ZOOM_IN_SCALE, self.ZOOM_IN_SCALE)
        elif delta < 0:
            self.scale(1/self.ZOOM_IN_SCALE, 1/self.ZOOM_IN_SCALE)

    def fit_in_view(self):
        """
        Fit in view
        """
        self.ensureVisible(self.scene().itemsBoundingRect())
        self.fitInView(self.scene().itemsBoundingRect(), Qt.KeepAspectRatio)



# class ModelGraphViewer(Gtk.DrawingArea):
#     def __init__(self):
#         super(ModelGraphViewer, self).__init__()
#
#         # Affine transform params
#         self.scaling_factor = 1
#         self.translation = [0, 0]
#
#         self.in_drag = False
#
#         # Default is generic visualization
#         self.vis_type_custom = False
#
#         self.model = None
#
#         # Events and handlers
#         self.add_events(Gdk.EventMask.SCROLL_MASK)
#         self.add_events(Gdk.EventMask.POINTER_MOTION_MASK)
#         self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
#         self.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
#         self.connect("draw", self.on_draw)
#         self.connect("scroll-event", self.on_wheel)
#         self.connect("button-press-event", self.on_button_press)
#         self.connect("button-release-event", self.on_button_release)
#         self.connect("motion-notify-event", self.on_mouse_move)
#
#         self.handle = Rsvg.Handle()
#
#     def on_draw(self, draw_area, cairo_context):
#         # Remember current cairo context
#         self.cairo_context = cairo_context
#
#         cairo_context.scale(self.scaling_factor, self.scaling_factor)
#         cairo_context.translate(*self.translation)
#         self.handle.render_cairo(cairo_context)
#
#     def on_wheel(self, source, event):
#         """
#         On wheel do point zoom.
#         """
#
#         def to_user(x, y):
#             cairo_context = self.get_window().cairo_create()
#             cairo_context.scale(self.scaling_factor, self.scaling_factor)
#             cairo_context.translate(*self.translation)
#             userx, usery = cairo_context.device_to_user(x, y)
#             return userx, usery
#
#         # Remember mouse location in user-space
#         old_x, old_y = to_user(event.x, event.y)
#
#         if event.direction == Gdk.ScrollDirection.UP:
#             self.scaling_factor *= 1.1
#         else:
#             self.scaling_factor /= 1.1
#
#         # limit scaling
#         if self.scaling_factor > 3:
#             self.scaling_factor = 3
#         elif self.scaling_factor < 0.05:
#             self.scaling_factor = 0.05
#
#         # Calculate new user coodinate
#         new_x, new_y = to_user(event.x, event.y)
#
#         # Do the translation correction for zoom-in-point effect
#         self.translation[0] += new_x - old_x
#         self.translation[1] += new_y - old_y
#
#         self.queue_draw()
#
#     def on_button_press(self, source, event):
#         """
#         On left mouse press enter drag mode and save state.
#         """
#
#         if event.button == Gdk.BUTTON_PRIMARY:
#             self.in_drag = True
#
#             # Save current pointer coordinates and translation
#             self.drag_start = (event.x, event.y)
#             self.drag_translation = self.translation[:]
#
#     def on_button_release(self, source, event):
#         """
#         On mouse button relese leave drag mode.
#         """
#
#         if event.button == Gdk.BUTTON_PRIMARY:
#             self.in_drag = False
#
#     def on_mouse_move(self, source, event):
#         """
#         Update translation vector on mouse move if the
#         user is grabbing the canvas (holding down left mouse button)
#         """
#
#         if self.in_drag:
#             # Update translation vector by the scaled mouse move
#             self.translation = [
#                 self.drag_translation[0] +
#                 1/self.scaling_factor * (event.x - self.drag_start[0]),
#                 self.drag_translation[1] +
#                 1/self.scaling_factor * (event.y - self.drag_start[1])]
#
#             self.queue_draw()
#
#     def set_vis_type(self, vis_type_custom):
#         self.vis_type_custom = vis_type_custom
#         self.update_image()
#
#     def get_vis_type(self):
#         return self.vis_type_custom
#
#     def best_fit(self):
#         """
#         Sets scaling and translation such that the image
#         is visible and occupies as much available space as possible.
#         """
#
#         if not self.model:
#             return
#
#         image_width = self.handle.props.width
#         image_height = self.handle.props.height
#         widget_width = self.get_allocation().width
#         widget_height = self.get_allocation().height
#
#         if float(image_height)/image_width > float(widget_height)/widget_width:
#             # Heights should be the same
#             self.scaling_factor = float(widget_height)/image_height
#             # Translate horizontaly
#             self.translation =\
#                 [float(widget_width)/self.scaling_factor/2
#                  - float(image_width)/2, 0]
#
#         else:
#             # Widths should be the same
#             self.scaling_factor = float(widget_width)/image_width
#             # Translate verticaly
#             self.translation =\
#                 [0, float(widget_height)/self.scaling_factor/2
#                  - float(image_height)/2]
#
#         self.queue_draw()
#
#     def update_image(self):
#
#         if not self.model:
#             return
#
#         dot_file = str(uuid.uuid4())
#         if self.vis_type_custom:
#             custom_export(self.model, dot_file)
#         else:
#             model_export(self.model, dot_file)
#
#         svg_file = "%s.svg" % dot_file
#         call(["dot", "-Tsvg", "-O", dot_file])
#         # Get rsvg handle for file
#         self.handle = Rsvg.Handle.new_from_file(svg_file)
#         os.remove(svg_file)
#         os.remove(dot_file)
#
#         self.queue_draw()
#
#     def update_model(self, model):
#         self.model = model
#         self.update_image()

