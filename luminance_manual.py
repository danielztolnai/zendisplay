"""Get ambient lighting data from user input"""
from luminance_sources import LuminanceSource

class LuminanceManual(LuminanceSource):
    """Get ambient lighting information from user input"""
    PARAMETER_BRIGHTNESS = 'value'
    PARAMETER_LUMINANCE_MIN = 'min'
    PARAMETER_LUMINANCE_MAX = 'max'
    BRIGHTNESS_INCREMENT = 5

    def __init__(self, name=None, path=None, brightness=50, luminance_range=(0, 100)):
        super().__init__(name, path)
        self.brightness = brightness
        self.luminance_min = luminance_range[0]
        self.luminance_max = luminance_range[1]

    @classmethod
    def detect(cls, parameters):
        """Add given MQTT configuration"""
        value = parameters[cls.PARAMETER_BRIGHTNESS]
        value_min = parameters[cls.PARAMETER_LUMINANCE_MIN]
        value_max = parameters[cls.PARAMETER_LUMINANCE_MAX]
        yield cls(
            name="manual",
            path="manual",
            brightness=value,
            luminance_range=(value_min, value_max),
        )

    def get_luminance(self):
        """Calculate luminance data from brightness"""
        luminance_range = self.luminance_max - self.luminance_min
        return ((self.brightness / 100) * luminance_range) + self.luminance_min

    def increase(self):
        """Increase the luminance"""
        self.brightness = min(self.brightness + self.BRIGHTNESS_INCREMENT, 100)
        return self.brightness

    def decrease(self):
        """Decrease the luminance"""
        self.brightness = max(self.brightness - self.BRIGHTNESS_INCREMENT, 0)
        return self.brightness

    def set(self, luminance):
        """Set the luminance to a given value"""
        self.brightness = max(min(luminance, 100), 0)
