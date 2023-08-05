#!/bin/python
import gi

gi.require_version("Gtk", "3.0")
import gi.repository.Gtk as Gtk
import gi.repository.Gdk as Gdk
from fancychat.TitleBar import TitleBar
from fancychat.ScrollView import ScrollView
from fancychat.MsgArrive import MsgArrive
from fancychat.MsgSend import MsgSend
from fancychat.Editor import Editor


class Restaurantic(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Fancy Chat")
        self.set_resizable(False)
        self.set_default_size(360, 512)

        self._container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self._container)

        self.title_bar = TitleBar()
        self._container.pack_start(self.title_bar, False, True, 0)

        self.scroll_view = ScrollView()
        self._container.pack_start(self.scroll_view, True, True, 0)

        self.scroll_view.append(MsgArrive("Message arrive..."))
        self.scroll_view.append(MsgSend("Message send..."))

        self.editor = Editor()
        self._container.pack_start(self.editor, False, False, 0)


if __name__ == '__main__':
    style_provider = Gtk.CssProvider()
    style_provider.load_from_path("share/fancychat/styles.css")

    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(),
        style_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

    window = Restaurantic()
    window.connect("delete-event", Gtk.main_quit)
    window.show_all()
    Gtk.main()
