import gi
gi.require_version("Gtk", "3.0")
import gi.repository.Gtk as Gtk
import gi.repository.GdkPixbuf as GdkPixbuf

class MsgArrive(Gtk.Box):
    def __init__(self, Msg):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

        self.avatar = Gtk.Image()
        self.avatar.set_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename="share/fancychat/preferences-desktop-emoticons.svg",
            width=48,
            height=48,
            preserve_aspect_ratio=True
        ))

        self.msg = Gtk.Label(Msg)
        self.msg.get_style_context().add_class("msg-text-arrive")
        #self.msg.set_halign(Gtk.Align.END)
        self.msg.set_justify(Gtk.Justification.RIGHT)
        self.msg.set_line_wrap(True)

        self.pack_start(self.avatar, False, False, 0)
        self.pack_start(self.msg, True, True, 0)