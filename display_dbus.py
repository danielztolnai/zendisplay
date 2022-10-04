"""Wrapper module for dbus brightness"""
import dbus
from base_classes import Display

class DisplayDBus(Display):
    """Handle displays through dbus"""
    DBUS_METHODS = [
        {
            'name': 'Cinnamon',
            'bus': 'org.cinnamon.SettingsDaemon.Power.Screen',
            'path': '/org/cinnamon/SettingsDaemon/Power',
            'get_method': 'GetPercentage',
            'set_method': 'SetPercentage',
        },
        {
            'name': 'Gnome',
            'bus': 'org.gnome.SettingsDaemon.Power.Screen',
            'path': '/org/gnome/SettingsDaemon/Power',
            'get_method': 'GetPercentage',
            'set_method': 'SetPercentage',
        },
        {
            'name': 'KDE',
            'bus': 'org.kde.Solid.PowerManagement',
            'path': '/org/kde/Solid/PowerManagement',
            'get_method': 'brightness',
            'set_method': 'setBrightness',
        },
    ]

    def __init__(self, name=None, path=None, func_rw=None):
        super().__init__(name, path)
        self.enabled = False
        self.func_get = func_rw[0]
        self.func_set = func_rw[1]

    @classmethod
    def detect(cls, parameters=None):
        """Find dbus control"""
        bus = dbus.SessionBus()
        for method in cls.DBUS_METHODS:
            try:
                iface = dbus.Interface(
                    bus.get_object(method['bus'], method['path']),
                    dbus_interface=method['bus'],
                )
                func_get = getattr(iface, method['get_method'])
                func_set = getattr(iface, method['set_method'])
                func_get()
                yield cls(name=method['name'], path="dbus", func_rw=(func_get, func_set))
            except dbus.exceptions.DBusException:
                pass

    def get_brightness(self):
        """Return last brightness value"""
        if self.enabled:
            return int(self.func_get())
        return None

    def _set_brightness(self, brightness):
        self.func_set(dbus.UInt32(brightness))
