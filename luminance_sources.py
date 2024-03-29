"""Get ambient lighting from system sensors"""
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
