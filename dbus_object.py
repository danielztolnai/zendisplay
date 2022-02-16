"""DBus helper classes"""
import dbus

class DBusObjectFreeDesktop:
    """Base DBus object"""
    def __init__(self, bus):
        self.bus = bus
        self.bus_name = 'org.freedesktop.DBus'
        self.path = '/org/freedesktop/DBus'
        self.interface_properties = 'org.freedesktop.DBus.Properties'

    def interface(self, dbus_interface=None):
        """Get interface to the object"""
        return dbus.Interface(
            self.bus.get_object(self.bus_name, self.path),
            dbus_interface=dbus_interface or self.bus_name,
        )

    def add_signal_receiver(self, **signal):
        """Connect a signal"""
        self.bus.add_signal_receiver(**{
            'dbus_interface': self.bus_name,
            'bus_name': self.bus_name,
            'path': self.path,
            **signal,
        })


class DBusObject(DBusObjectFreeDesktop):
    """DBus helper object to represent an object on the bus"""
    def __init__(self, bus, bus_name, path):
        super().__init__(bus)
        self.bus_name = bus_name
        self.path = path
        self.fd_dbus = DBusObjectFreeDesktop(bus)
        self.callbacks = {
            'appear': None,
            'vanish': None,
            'property_change': None,
        }

    def __callback(self, callback_name, *args, **kwargs):
        """Run a callback if it is callable"""
        callback = self.callbacks[callback_name]
        if callable(callback):
            callback(*args, **kwargs)

    ### Properties
    def get_property(self, property_name):
        """Get the value of a property"""
        return self.interface(self.interface_properties).Get(self.bus_name, property_name)

    def set_property(self, property_name, value):
        """Set the value of a property"""
        self.interface(self.interface_properties).Set(self.bus_name, property_name, value)

    def watch_properties(self, callback):
        """Connect a callback to the PropertiesChanged signal"""
        self.watch_properties_stop()
        self.callbacks['property_change'] = callback

        self.add_signal_receiver(
            handler_function=self.__handle_property_change,
            signal_name='PropertiesChanged',
            dbus_interface=self.interface_properties,
        )

    def watch_properties_stop(self):
        """Stop listening to property changes"""
        self.bus.remove_signal_receiver(self.__handle_property_change)
        self.callbacks['property_change'] = None

    def __handle_property_change(self, *args, **kwargs):
        """Handle property changes"""
        self.__callback('property_change', *args, **kwargs)

    ### Object presence on bus
    def exists(self):
        """Return whether the object is present on the bus"""
        return self.fd_dbus.interface().NameHasOwner(self.bus_name)

    def watch_name(self, callback_appear, callback_vanish):
        """Connect callbacks to object appearing / vanishing"""
        self.watch_name_stop()
        self.callbacks['appear'] = callback_appear
        self.callbacks['vanish'] = callback_vanish
        self.fd_dbus.add_signal_receiver(
            handler_function=self.__handle_name_change,
            signal_name='NameOwnerChanged',
            arg0=self.bus_name,
        )

    def watch_name_stop(self):
        """Stop listening to the object appearing / vanishing"""
        self.bus.remove_signal_receiver(self.__handle_name_change)
        self.callbacks['appear'] = None
        self.callbacks['vanish'] = None

    def __handle_name_change(self, _name, old_owner, new_owner):
        """Handle object appearing / vanishing"""
        if new_owner and not old_owner:
            self.__callback('appear')
        if old_owner and not new_owner:
            self.__callback('vanish')
