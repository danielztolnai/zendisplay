#!/usr/bin/env python3
"""Small script to adjust display brightness according to ambient lighting"""
import os
import sys
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from displays import DisplayManager
from display_dbus import DisplayDBus
from display_ddcutil import DisplayDDCUtil
from luminance_sources import LuminanceSourceManager
from luminance_dbus import LuminanceDBus
from luminance_iio import LuminanceIIO
from luminance_manual import LuminanceManual
from luminance_mqtt import LuminanceMQTT

DEFAULT_SENSOR = 0
SHOW_NOTIFICATIONS = False
MQTT_HOST = None
MQTT_TOPIC = None
MQTT_PUBLISH = False

class Controller:
    """Recommends new brightness value based on current data"""
    BRIGHTNESS_INCREMENT = 5

    def __init__(self):
        self.brightness_margin = 5
        self.line_m = 0.2
        self.line_b = 0

    def calculate_brightness(self, luminance):
        """Calculate brightness from ambient lighting"""
        value = round(self.line_m * luminance + self.line_b)
        return max(min(100, value), 0)

    def brightness_should_change(self, old_brightness, new_brightness):
        """Determine whether the brightness should be changed"""
        if old_brightness == new_brightness:
            return False

        if new_brightness in (0, 100):
            return True

        return abs(old_brightness - new_brightness) >= self.brightness_margin

    def recommend_brightness(self, current_luminance, current_brightness):
        """Get a new brightness value based on current data"""
        recommended_brightness = self.calculate_brightness(current_luminance)

        if not self.brightness_should_change(current_brightness, recommended_brightness):
            return current_brightness

        print("Brightness: {:3d}% -> {:3d}% (luminance: {:.1f} lx)".format(
            current_brightness,
            recommended_brightness,
            current_luminance
        ))

        return recommended_brightness

    def set_intercept(self, value):
        """Set the slope of the brightness function"""
        self.line_b = value

    def increase_intercept(self):
        """Increase brightness function intercept"""
        self.line_b = min(self.line_b + self.BRIGHTNESS_INCREMENT, 100)
        return self.line_b

    def decrease_intercept(self):
        """Decrease brightness function intercept"""
        self.line_b = max(self.line_b - self.BRIGHTNESS_INCREMENT, 0)
        return self.line_b


class ZenDisplay(QtWidgets.QSystemTrayIcon):
    """System tray icon class"""
    def __init__(self):
        super().__init__()

        self.controller = Controller()

        self.displays = DisplayManager()
        self.displays.add_displays_type(DisplayDDCUtil)
        self.displays.add_displays_type(DisplayDBus)

        if len(self.displays) == 0:
            print('Could not find supported displays')
            sys.exit()

        self.sensors = LuminanceSourceManager()
        self.sensors.add_source_type(LuminanceDBus)
        self.sensors.add_source_type(LuminanceIIO)
        self.sensors.add_source_type(LuminanceMQTT, {'topic': MQTT_TOPIC, 'host': MQTT_HOST})
        manual_parameters = self.controller.get_range()
        manual_parameters.update({'value': self.displays.get_brightness()})
        self.sensors.add_source_type(LuminanceManual, manual_parameters)
        self.sensors.activate(DEFAULT_SENSOR)

        self.menu = self.construct_menu()
        self.menu_visible = False
        self.setContextMenu(self.menu)
        self.activated.connect(lambda reason: self.action_click(reason, self))

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.main_control)
        self.timer.start(1000)

        if MQTT_PUBLISH is True:
            self.mqtt_publisher = LuminanceMQTT(name="mqttp", path=MQTT_TOPIC, host=MQTT_HOST)

    def toggle_menu(self):
        """Toggle context menu visibility"""
        if self.menu_visible:
            self.menu.hide()
        else:
            self.menu.popup(QtGui.QCursor.pos())
        self.menu_visible = not self.menu_visible

    def construct_menu(self):
        """Construct a menu from the sitemap"""
        menu = QtWidgets.QMenu()
        self.construct_menu_displays(menu)
        self.construct_menu_sensors(menu)
        self.construct_menu_brightness(menu)

        # Create quit button
        menu.addSeparator()
        action_quit = menu.addAction("Quit")
        action_quit.triggered.connect(lambda _: sys.exit())
        return menu

    def construct_menu_displays(self, parent):
        """Create submenu for displays"""
        display_menu = parent.addMenu('Displays')
        for display in self.displays:
            action = display_menu.addAction(display.name + " (" + display.path + ")")
            action.setCheckable(True)
            action.setChecked(display.enabled)
            did = display.uid
            action.triggered.connect(lambda state, did=did: self.displays.set_active(did, state))

    def construct_menu_sensors(self, parent):
        """Create submenu for sensors"""
        sensor_menu = parent.addMenu('Sensors')
        sensor_group = QtWidgets.QActionGroup(sensor_menu, exclusive=True)
        for sensor in self.sensors:
            action = sensor_menu.addAction(sensor.name + " (" + sensor.path + ")")
            action.setCheckable(True)
            if sensor.uid == self.sensors.get_active():
                action.setChecked(True)
            sid = sensor.uid
            action.triggered.connect(lambda _, sid=sid: self.sensors.activate(sid))
            sensor_group.addAction(action)

    def construct_menu_brightness(self, parent):
        """Create submenu for the brightness setting"""
        brightness_menu = parent.addMenu('Brightness')
        for value in range(0, 101, 10):
            action = brightness_menu.addAction(str(value) + "%")
            action.triggered.connect(lambda _, value=value: self.controller.set_intercept(value))

    def main_control(self):
        """Main control function, sets display brightness dynamically"""
        if not self.sensors.is_ready():
            return

        luminance = self.sensors.get_luminance()
        current_brightness = self.displays.get_brightness()
        recommended_brightness = self.controller.recommend_brightness(luminance, current_brightness)

        if recommended_brightness == current_brightness:
            return

        self.setToolTip('Brightness: ' + str(recommended_brightness) + '%')
        self.displays.set_brightness(recommended_brightness)
        if MQTT_PUBLISH is True:
            self.mqtt_publisher.publish(luminance)

    def event(self, event):
        """Event handler for QEvent objects"""
        if event.type() == QtCore.QEvent.Wheel:
            new_value = None
            if event.angleDelta().y() < 0:
                new_value = self.controller.decrease_intercept()
            else:
                new_value = self.controller.increase_intercept()
            if new_value is not None and self.supportsMessages() and SHOW_NOTIFICATIONS:
                self.showMessage('Brightness', str(new_value) + '%', msecs=500)
            return True
        return False

    @classmethod
    @QtCore.pyqtSlot()
    def action_click(cls, reason, tray):
        """Toggle menu on click"""
        if reason in [QtWidgets.QSystemTrayIcon.Trigger, QtWidgets.QSystemTrayIcon.Context]:
            tray.toggle_menu()


def main():
    """Entrypoint when running in standalone mode"""
    def get_icon():
        """Get theme icon or fallback to local one"""
        icon = QtGui.QIcon.fromTheme('video-display-symbolic')
        if icon.isNull():
            return QtGui.QIcon(os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "icon.png",
            ))
        return icon

    app = QtWidgets.QApplication([])
    app.setQuitOnLastWindowClosed(False)
    zendisplay = ZenDisplay()
    zendisplay.setIcon(get_icon())
    zendisplay.show()
    app.exec_()


if __name__ == "__main__":
    main()
