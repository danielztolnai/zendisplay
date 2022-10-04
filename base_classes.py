"""Base classes for sources and targets"""
class ZenDisplayObject:
    """Base class for sources and targets"""
    def __init__(self, name=None, path=None):
        self.uid = None
        self.name = name
        self.path = path
        self.enabled = True

    @classmethod
    def detect(cls, parameters):
        """Find all objects of this type connected to the system"""

    def enable(self):
        """Enable the object"""
        self.enabled = True

    def disable(self):
        """Disable the object"""
        self.enabled = False


class LuminanceSource(ZenDisplayObject):
    """Base class for luminance data sources"""
    def __init__(self, name=None, path=None):
        super().__init__(name=name, path=path)
        self.__ready = False

    def is_ready(self):
        """Return whether the source is ready to be used"""
        return self.__ready

    def get_luminance(self):
        """Get luminance from the source"""

    def _set_ready(self, is_ready):
        """Set the ready flag"""
        self.__ready = is_ready


class Display(ZenDisplayObject):
    """Base class for displays"""
    def get_brightness(self):
        """Get current brightness of the display"""

    def set_brightness(self, brightness):
        """Set brightness of the display"""
        if brightness == self.get_brightness():
            return
        if brightness > 100 or brightness < 0:
            return

        if self.enabled:
            self._set_brightness(brightness)

    def _set_brightness(self, brightness):
        """Set brightness of the underlying device"""
