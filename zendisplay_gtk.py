"""Small script to adjust display brightness according to ambient lighting"""
# pylint: disable=wrong-import-position,wrong-import-order
import sys
import gi
from dbus.mainloop.glib import DBusGMainLoop
from zendisplay_base import ZenDisplay as ZenDisplayBase
from zendisplay_config import Config

gi.require_version('Gtk', '3.0')
gi.require_version('AyatanaAppIndicator3', '0.1')
from gi.repository import AyatanaAppIndicator3 as appindicator
from gi.repository import Gtk as gtk
from gi.repository import GLib

class ZenDisplay(ZenDisplayBase):
    """System tray icon class"""
    def __init__(self):
        ZenDisplayBase.__init__(self)

        self.menu = self.construct_menu()
        self.indicator.set_menu(self.menu)
        self.indicator.connect("scroll_event", self._scroll_event)
        self._brightness_updated(self.displays.get_brightness())

    def run(self):
        """Run main loop"""
        gtk.main()

    def _init_framework(self):
        """Initialize the main loop"""
        self.indicator = self._create_indicator()
        DBusGMainLoop(set_as_default=True)
        GLib.timeout_add(1000, self.main_control)

    def _brightness_updated(self, brightness):
        """Run when brightness is updated"""
        self.indicator.set_title('Brightness: ' + str(brightness) + '%')

    @staticmethod
    def _create_indicator():
        indicator = appindicator.Indicator.new(
            "ZenDisplay",
            "video-display-symbolic",
            appindicator.IndicatorCategory.APPLICATION_STATUS,
        )
        indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        return indicator

    def construct_menu(self):
        """Construct the menu"""
        menu = gtk.Menu()
        self.construct_menu_displays(menu)
        self.construct_menu_sensors(menu)
        self.construct_menu_brightness(menu)
        self._construct_menu_separator(menu)
        self._construct_menu_condition_checker(menu)
        self._construct_menu_separator(menu)
        self._construct_menu_save(menu)
        self._construct_menu_quit(menu)
        menu.show()
        return menu

    @classmethod
    def _construct_menu_separator(cls, parent):
        """Create a separator menu item"""
        separator = gtk.SeparatorMenuItem()
        separator.show()
        parent.append(separator)

    def _construct_menu_condition_checker(self, parent):
        """Create condition checker checkbox"""
        action = gtk.CheckMenuItem(label="Condition checker")
        action.set_active(self.condition_checker.is_enabled())
        action.connect(
            'toggled',
            lambda item: self.condition_checker.set_enabled(item.get_active())
        )
        action.show()
        parent.append(action)

    @classmethod
    def _construct_menu_save(cls, parent):
        """Create save button"""
        action = gtk.MenuItem(label="Save settings")
        action.connect("activate", lambda _: Config().save())
        action.show()
        parent.append(action)

    @classmethod
    def _construct_menu_quit(cls, parent):
        """Create quit button"""
        action = gtk.MenuItem(label="Quit")
        action.connect("activate", lambda _: sys.exit())
        action.show()
        parent.append(action)

    def construct_menu_displays(self, parent):
        """Create submenu for displays"""
        display_menu = gtk.Menu()
        display_menu_action = gtk.MenuItem(label="Displays")
        display_menu_action.set_submenu(display_menu)
        display_menu_action.show()
        parent.append(display_menu_action)

        for display in self.displays:
            action = gtk.CheckMenuItem(label=display.name + " (" + display.path + ")")
            action.set_active(display.enabled)
            did = display.uid
            action.connect(
                'toggled',
                lambda item, did=did: self.displays.set_active(did, item.get_active())
            )
            action.show()
            display_menu.append(action)

    def construct_menu_sensors(self, parent):
        """Create submenu for sensors"""
        sensor_menu = gtk.Menu()
        sensor_menu_action = gtk.MenuItem(label="Sensors")
        sensor_menu_action.set_submenu(sensor_menu)
        sensor_menu_action.show()
        parent.append(sensor_menu_action)

        for sensor in self.sensors:
            action = gtk.RadioMenuItem(label=sensor.name + " (" + sensor.path + ")")
            action.join_group((sensor_menu.get_children()[:1] or [None])[0])
            if sensor.uid == self.sensors.get_active():
                action.set_active(True)
            sid = sensor.uid
            action.connect('activate', lambda _, sid=sid: self.sensors.activate(sid))
            action.show()
            sensor_menu.append(action)

    def construct_menu_brightness(self, parent):
        """Create submenu for the brightness setting"""
        brightness_menu = gtk.Menu()
        brightness_menu_action = gtk.MenuItem(label='Brightness')
        brightness_menu_action.set_submenu(brightness_menu)
        brightness_menu_action.show()
        parent.append(brightness_menu_action)

        for value in range(0, 101, 10):
            action = gtk.RadioMenuItem(label=str(value) + "%")
            action.join_group((brightness_menu.get_children()[:1] or [None])[0])
            if value == Config().get('brightness', 'base_value'):
                action.set_active(True)
            action.connect('activate', lambda _, value=value: self.controller.set_intercept(value))
            action.show()
            brightness_menu.append(action)

    def _scroll_event(self, _1, _2, direction):
        """Event handler for the scroll_event signal"""
        if direction == 0:
            self.controller.increase_intercept()
        elif direction == 1:
            self.controller.decrease_intercept()
