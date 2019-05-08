#!/usr/bin/env python3
"""Small script to adjust display brightness according to ambient lighting"""
import os
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from displays import Displays
from luminance_sources import LuminanceSourceManager
from luminance_iio import LuminanceIIO

class Controller:
    """Recommends new brightness value based on current data"""
    def __init__(self):
        self.brightness_margin = 5
        self.line_m = 0.1151079
        self.line_b = 30.61871

    def calculate_brightness(self, luminance):
        """Calculate brightness from ambient lighting"""
        value = round(self.line_m * luminance + self.line_b)
        return max(min(100, value), 0)

    def recommend_brightness(self, current_luminance, current_brightness):
        """Get a new brightness value based on current data"""
        recommended_brightness = self.calculate_brightness(current_luminance)
        if abs(current_brightness - recommended_brightness) < self.brightness_margin:
            recommended_brightness = current_brightness
        else:
            print("Brightness: ", end='')
            print(str(current_brightness) + "% -> " + str(recommended_brightness) + "% ", end='')
            print("(luminance: " + str(current_luminance) + " lx)")
        return recommended_brightness


class ZenDisplay(QtWidgets.QSystemTrayIcon):
    """System tray icon class"""
    def __init__(self):
        super().__init__()
        self.sensors = LuminanceSourceManager()
        self.sensors.add_source_type(LuminanceIIO)
        self.displays = Displays()
        self.controller = Controller()

        self.menu = self.construct_menu()
        self.menu_visible = False
        self.setContextMenu(self.menu)
        self.activated.connect(lambda reason: self.action_click(reason, self))

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.main_control)
        self.timer.start(1000)

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

        # Create quit button
        menu.addSeparator()
        action_quit = menu.addAction("Quit")
        action_quit.triggered.connect(lambda _: quit())
        return menu

    def construct_menu_displays(self, parent):
        """Create submenu for displays"""
        display_menu = parent.addMenu('Displays')
        for display in self.displays:
            action = display_menu.addAction(display['name'])
            action.setCheckable(True)
            action.setChecked(display['use'])
            did = display['id']
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
            action.triggered.connect(lambda state, sid=sid: self.sensors.activate(sid))
            sensor_group.addAction(action)

    def main_control(self):
        """Main control function, sets display brightness dynamically"""
        luminance = self.sensors.get_luminance()
        current_brightness = self.displays.get_brightness()
        recommended_brightness = self.controller.recommend_brightness(luminance, current_brightness)
        self.displays.set_brightness(recommended_brightness)

    @classmethod
    @QtCore.pyqtSlot()
    def action_click(cls, reason, tray):
        """Toggle menu on click"""
        if reason in [QtWidgets.QSystemTrayIcon.Trigger, QtWidgets.QSystemTrayIcon.Context]:
            tray.toggle_menu()


APP = QtWidgets.QApplication([])
APP.setQuitOnLastWindowClosed(False)
ZENDISPLAY = ZenDisplay()
ZENDISPLAY.setIcon(QtGui.QIcon(os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "icon.png",
)))
ZENDISPLAY.show()
APP.exec_()
