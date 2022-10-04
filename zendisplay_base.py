"""Small script to adjust display brightness according to ambient lighting"""
import sys
from zendisplay_config import Config
from controller import Controller
from displays import DisplayManager
from display_dbus import DisplayDBus
from display_ddcutil import DisplayDDCUtil
from luminance_sources import LuminanceSourceManager
from luminance_dbus import LuminanceDBus
from luminance_iio import LuminanceIIO
from luminance_manual import LuminanceManual
from luminance_mqtt import LuminanceMQTT

class ZenDisplay:
    """Automatic display brightness controller"""
    def __init__(self):
        self._init_framework()

        self.controller = Controller()
        self.displays = self._init_displays()
        self.sensors = self._init_sensors()

    def run(self):
        """Run main loop"""

    def _init_framework(self):
        """Initialize the main loop"""

    def _brightness_updated(self, brightness):
        """Run when brightness is updated"""

    @staticmethod
    def _init_displays():
        displays = DisplayManager()
        displays.add_displays_type(DisplayDDCUtil)
        displays.add_displays_type(DisplayDBus)

        if Config().get('mqtt', 'publish') is True:
            displays.add_displays_type(LuminanceMQTT)

        if len(displays) == 0:
            print('Could not find supported displays')
            sys.exit()

        return displays

    def _init_sensors(self):
        sensors = LuminanceSourceManager()
        sensors.add_source_type(LuminanceDBus)
        sensors.add_source_type(LuminanceIIO)

        if Config().get('mqtt', 'subscribe') is True:
            sensors.add_source_type(LuminanceMQTT)

        sensors.add_source_type(LuminanceManual, {
            'cb_enable': lambda: self.controller.set_intercept(self.displays.get_brightness()),
            'cb_disable': self.controller.set_intercept,
            'get_value': lambda: self.controller.line_b,
        })

        sensors.activate(Config().get('general', 'default_sensor'))

        return sensors

    def _is_ready(self):
        return self.sensors.is_ready() and self.displays.is_ready()

    def main_control(self):
        """Main control function, sets display brightness dynamically"""
        if not self._is_ready():
            return True

        recommended_brightness = self.controller.recommend_brightness(
            self.sensors.get_luminance(),
            self.displays.get_brightness(),
        )

        if recommended_brightness is None:
            return True

        self.displays.set_brightness(recommended_brightness)
        self._brightness_updated(recommended_brightness)
        return True
