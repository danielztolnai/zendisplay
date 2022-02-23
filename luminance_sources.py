"""Get ambient lighting from system sensors"""
class LuminanceSource:
    """Base class for luminance data sources"""
    def __init__(self, name=None, path=None):
        self.uid = None
        self.name = name
        self.path = path
        self.__ready = True

    @classmethod
    def detect(cls, parameters):
        """Find all sources of this type connected to the system"""

    def is_ready(self):
        """Return whether the source is ready to be used"""
        return self.__ready

    def get_luminance(self):
        """Get luminance from the source"""

    def enable(self):
        """Enable the source"""

    def disable(self):
        """Disable the source"""


class LuminanceSourceManager:
    """Handle ambient lighting sources"""
    def __init__(self):
        self.iter_id = 0
        self.active = 0
        self.sensors = []

    def __iter__(self):
        self.iter_id = 0
        return self

    def __next__(self):
        if self.iter_id >= len(self.sensors):
            raise StopIteration
        result = self.sensors[self.iter_id]
        self.iter_id += 1
        return result

    def __getitem__(self, key):
        return self.sensors[key]

    def __len__(self):
        return len(self.sensors)

    def add_source_type(self, source_class, parameters=None):
        """Find all sensors of the given type connected to the system"""
        for source in source_class.detect(parameters):
            self.add_source(source)

    def add_source(self, source):
        """Add a new source"""
        source.uid = len(self.sensors)
        self.sensors.append(source)
        return source.uid

    def get_luminance(self):
        """Get luminance from the active sensor"""
        return self.sensors[self.active].get_luminance()

    def is_ready(self):
        """Get ready status from the active sensor"""
        return self.sensors[self.active].is_ready()

    def activate(self, sensor_id):
        """Use the source with the given ID"""
        self.sensors[self.active].disable()
        self.active = sensor_id
        self.sensors[self.active].enable()

    def get_active(self):
        """Get id of the active source"""
        return self.active
