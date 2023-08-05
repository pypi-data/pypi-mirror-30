import gi
gi.require_version("Gtk", "3.0")
import gi.repository.Gtk as Gtk
import gi.repository.GdkPixbuf as GdkPixbuf

class Editor(Gtk.Box):
    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.set_margin_bottom(6)

        self.cam_image = Gtk.Image()
        self.cam_image.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename="share/fancychat/kphotoalbum.svg",
            width=32,
            height=32,
            preserve_aspect_ratio=True
        ))
        self.button_cam = Gtk.Button()
        self.button_cam.set_image(self.cam_image)

        self.input = Gtk.Entry()
        self.input.set_placeholder_text("Type your message...")

        self.send_image = Gtk.Image()
        self.send_image.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename="share/fancychat/appbar.control.fastforward.variant.svg",
            width=32,
            height=32,
            preserve_aspect_ratio=True
        ))
        self.button_send = Gtk.Button()
        self.button_send.set_image(self.send_image)

        self.pack_start(self.button_cam, False, False, 0)
        self.pack_start(self.input, True, True, 0)
        self.pack_start(self.button_send, False, False, 0)