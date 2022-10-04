"""Logic to calculate the next display brightness value"""
from zendisplay_config import Config

class Controller:
    """Recommends new brightness value based on current data"""
    def __init__(self):
        self.brightness_increment = Config().get('brightness', 'increment')
        self.brightness_margin = Config().get('brightness', 'margin')
        self.line_m = Config().get('brightness', 'slope')
        self.line_b = Config().get('brightness', 'base_value')

    def calculate_brightness(self, luminance):
        """Calculate brightness from ambient lighting"""
        value = round(self.line_m * luminance + self.line_b)
        return max(min(100, value), 0)

    def brightness_should_change(self, old_brightness, new_brightness):
        """Determine whether the brightness should be changed"""
        if old_brightness == new_brightness:
            return False

        if new_brightness in (0, 100) or old_brightness is None:
            return True

        return abs(old_brightness - new_brightness) >= self.brightness_margin

    def recommend_brightness(self, current_luminance, current_brightness):
        """Get a new brightness value based on current data"""
        recommended_brightness = self.calculate_brightness(current_luminance)

        if not self.brightness_should_change(current_brightness, recommended_brightness):
            return None

        print((
            f'Brightness: {int(current_brightness or 0):3d}% -> '
            f'{recommended_brightness:3d}% '
            f'(luminance: {current_luminance:.1f} lx)'
        ))

        return recommended_brightness

    def set_intercept(self, value):
        """Set the slope of the brightness function"""
        self.line_b = value
        Config().set('brightness', 'base_value', str(value))

    def increase_intercept(self):
        """Increase brightness function intercept"""
        self.set_intercept(min(self.line_b + self.brightness_increment, 100))
        return self.line_b

    def decrease_intercept(self):
        """Decrease brightness function intercept"""
        self.set_intercept(max(self.line_b - self.brightness_increment, 0))
        return self.line_b
