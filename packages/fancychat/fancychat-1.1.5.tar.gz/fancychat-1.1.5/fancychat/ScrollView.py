import gi
gi.require_version("Gtk", "3.0")

import gi.repository.Gtk as Gtk

class ScrollView(Gtk.ScrolledWindow):
    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.ALWAYS)
        self.set_margin_top(6)
        self.set_margin_bottom(6)

        self.view_port = Gtk.Viewport()
        self.add(self.view_port)

        self._container = Gtk.VBox(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self._container.set_margin_left(16)
        self._container.set_margin_right(16)
        self.view_port.add(self._container)

    def append(self, MsgWidget):
        self._container.pack_start(MsgWidget, False, True, 0)