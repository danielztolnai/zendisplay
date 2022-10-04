"""Manage displays available in the system"""
class DisplayManager:
    """Manage all displays in the system"""
    def __init__(self):
        self.iter_id = 0
        self.displays = []

    def __iter__(self):
        self.iter_id = 0
        return self

    def __next__(self):
        if self.iter_id >= len(self.displays):
            raise StopIteration
        result = self.displays[self.iter_id]
        self.iter_id += 1
        return result

    def __getitem__(self, key):
        return self.displays[key]

    def __len__(self):
        return len(self.displays)

    def add_displays_type(self, display_class, parameters=None):
        """Find all displays of the given type connected to the system"""
        return [self.add_display(display) for display in display_class.detect(parameters)]

    def add_display(self, display):
        """Add a new source"""
        display.uid = len(self.displays)
        self.displays.append(display)
        return display.uid

    def get_brightness(self):
        """Return brightness value from first enabled display"""
        brightness = None
        for display in self.displays:
            brightness = display.get_brightness()
            if brightness is not None:
                return brightness
        return None

    def set_brightness(self, brightness):
        """Set brightness for displays"""
        for display in self.displays:
            display.set_brightness(brightness)

    def set_active(self, display_id, active):
        """Include/exclude display in the used displays list"""
        if bool(active):
            self.displays[display_id].enable()
        else:
            self.displays[display_id].disable()
