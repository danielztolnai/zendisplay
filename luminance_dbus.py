"""Get ambient lighting data through dbus from iio-sensor-proxy"""
from threading import Timer
import dbus
from dbus_object import DBusObject
from base_classes import LuminanceSource

class LuminanceDBus(LuminanceSource):
    """Get ambient lighting information from iio-sensor-proxy via dbus"""
    def __init__(self, name=None, path=None):
        super().__init__(name, path)
        self.luminance = 0
        self.luminance_prop = 'LightLevel'
        self.appear_timer = None

        # Configure DBus connection
        self.bus = dbus.SystemBus()
        self.sensor = DBusObject(self.bus, 'net.hadess.SensorProxy', '/net/hadess/SensorProxy')

        self.sensor.watch_name(self.sensor_connect, self.sensor_disconnect)
        if self.sensor.exists():
            self.sensor_connect()

    @classmethod
    def detect(cls, parameters):
        """Create iio-sensor-proxy connector"""
        yield cls(name="iio-sensor-proxy", path='dbus')

    def get_luminance(self):
        """Get last luminance data received"""
        return self.luminance

    def sensor_connect(self):
        """Attach sensor"""
        print(f'{self.name} appeared')
        self.sensor.watch_properties(self.handle_sensor_proxy_signal)
        self.sensor.interface().ClaimLight()
        self.appear_timer = Timer(1.0, self.sensor_read)
        self.appear_timer.start()

    def sensor_read(self):
        """Read sensor manually"""
        self.luminance = self.sensor.get_property(self.luminance_prop)
        self._set_ready(True)
        print(f'{self.name} ready')

    def sensor_disconnect(self):
        """Detach sensor"""
        print(f'{self.name} vanished')
        if self.appear_timer:
            self.appear_timer.cancel()
        self._set_ready(False)
        self.sensor.watch_properties_stop()

    def handle_sensor_proxy_signal(self, _interface_name, changed_props, _invalidated_props):
        """Read luminance value from incoming DBus signal"""
        if self.luminance_prop in changed_props:
            self.luminance = changed_props[self.luminance_prop]
