import gi
gi.require_version("Gtk", "3.0")
import gi.repository.Gtk as Gtk
import gi.repository.GdkPixbuf as GdkPixbuf


class TitleBar(Gtk.Box):
    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.get_style_context().add_class("japanese-indigo")
        self.get_style_context().add_class("header-box")

        self.logo = Gtk.Image()
        self.logo.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename="share/fancychat/fbmessenger.svg",
            width=32,
            height=32,
            preserve_aspect_ratio=True
        ))

        self.title = Gtk.Label("Messages")
        self.title.get_style_context().add_class("text-white")
        self.title.set_halign(Gtk.Align.START)

        self.menu = Gtk.Image()
        self.menu.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename="share/fancychat/appbar.lines.horizontal.4.svg",
            width=32,
            height=32,
            preserve_aspect_ratio=True
        ))

        self.pack_start(self.logo, False, True, 0)
        self.pack_start(self.title, True, True, 0)
        self.pack_start(self.menu, False, True, 0)
