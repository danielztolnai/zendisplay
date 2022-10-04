"""Small script to adjust display brightness according to ambient lighting"""
import os
import sys
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from dbus.mainloop.pyqt5 import DBusQtMainLoop
from zendisplay_base import ZenDisplay as ZenDisplayBase
from zendisplay_config import Config

class ZenDisplay(ZenDisplayBase, QtWidgets.QSystemTrayIcon):
    """System tray icon class"""
    def __init__(self):
        ZenDisplayBase.__init__(self)
        QtWidgets.QSystemTrayIcon.__init__(self)

        self.menu = self.construct_menu()
        self.menu_visible = False
        self.setContextMenu(self.menu)
        self.activated.connect(lambda reason: self.action_click(reason, self))
        self.setIcon(self._get_icon())
        self.show()
        self._brightness_updated(self.displays.get_brightness())

    def run(self):
        """Run main loop"""
        self.timer.start(1000)
        self.qt_app.exec_()

    def _init_framework(self):
        """Initialize the main loop"""
        self.qt_app = QtWidgets.QApplication([])
        self.qt_app.setQuitOnLastWindowClosed(False)
        DBusQtMainLoop(set_as_default=True)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.main_control)

    def _brightness_updated(self, brightness):
        """Run when brightness is updated"""
        self.setToolTip('Brightness: ' + str(brightness) + '%')

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
        action_save = menu.addAction("Save settings")
        action_save.triggered.connect(lambda _: Config().save())
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
        sensor_group = QtWidgets.QActionGroup(sensor_menu)
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
        brightness_group = QtWidgets.QActionGroup(brightness_menu)
        for value in range(0, 101, 10):
            action = brightness_menu.addAction(str(value) + "%")
            action.setCheckable(True)
            if value == Config().get('brightness', 'base_value'):
                action.setChecked(True)
            action.triggered.connect(lambda _, value=value: self.controller.set_intercept(value))
            brightness_group.addAction(action)

    def event(self, event):
        """Event handler for QEvent objects"""
        if event.type() == QtCore.QEvent.Wheel:
            new_value = None
            if event.angleDelta().y() < 0:
                new_value = self.controller.decrease_intercept()
            else:
                new_value = self.controller.increase_intercept()
            show_notification = Config().get('general', 'show_notifications')
            if new_value is not None and self.supportsMessages() and show_notification:
                self.showMessage('Brightness', str(new_value) + '%', msecs=500)
            return True
        return False

    @classmethod
    @QtCore.pyqtSlot()
    def action_click(cls, reason, tray):
        """Toggle menu on click"""
        if reason in [QtWidgets.QSystemTrayIcon.Trigger, QtWidgets.QSystemTrayIcon.Context]:
            tray.toggle_menu()

    @staticmethod
    def _get_icon():
        """Get theme icon or fallback to local one"""
        icon = QtGui.QIcon.fromTheme('video-display-symbolic')
        if icon.isNull():
            return QtGui.QIcon(os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "icon.png",
            ))
        return icon
