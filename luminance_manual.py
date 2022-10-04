"""Get ambient lighting data from user input"""
from base_classes import LuminanceSource

class LuminanceManual(LuminanceSource):
    """Manual luminance sensor that always returns 0 luminance"""
    def __init__(self, name=None, path=None, parameters=None):
        super().__init__(name, path)
        self._set_ready(True)
        self.original_value = 0
        self.callbacks = {
            'enable': parameters['cb_enable'],
            'disable': parameters['cb_disable'],
            'get_value': parameters['get_value']
        }

    @classmethod
    def detect(cls, parameters):
        """Create manual luminance source"""
        yield cls(name="manual", path="manual", parameters=parameters)

    def get_luminance(self):
        """Manual luminance is always 0, brightness is set by controller intercept"""
        return 0

    def enable(self):
        """Enable the source"""
        super().enable()
        self.original_value = self.__callback('get_value')
        self.__callback('enable')

    def disable(self):
        """Disable the source"""
        super().disable()
        self.__callback('disable', self.original_value)

    def __callback(self, callback_name, *args, **kwargs):
        """Run a callback if it is callable"""
        callback = self.callbacks[callback_name]
        if callable(callback):
            return callback(*args, **kwargs)
        return None
