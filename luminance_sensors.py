"""Get ambient lighting from system sensors"""
class LuminanceSensors:
    """Handle ambient lighting sensors through sysfs"""
    SYSFS_IIO_PATH = '/sys/bus/iio/devices/'
    SYSFS_IIO_ILLUMINANCE_FILE = 'in_illuminance_raw'
    SYSFS_IIO_NAME_FILE = 'name'

    def __init__(self):
        self.iter_id = 0
        self.active = 0
        self.sensors = []
        self.detect()

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

    def detect(self):
        """Find all sensors connected to the system"""
        import os
        directory = os.fsencode(self.SYSFS_IIO_PATH)
        for device in os.listdir(directory):
            device_path = os.path.join(self.SYSFS_IIO_PATH, os.fsdecode(device))
            # Check if device is an illuminance sensor
            if not os.path.isfile(os.path.join(device_path, self.SYSFS_IIO_ILLUMINANCE_FILE)):
                continue
            # Get name and add to list
            with open(os.path.join(device_path, self.SYSFS_IIO_NAME_FILE)) as file_in:
                device_name = file_in.read().strip()
                self.sensors.append({
                    'id': len(self.sensors),
                    'name': device_name,
                    'file': os.path.join(device_path, self.SYSFS_IIO_ILLUMINANCE_FILE),
                    'device': os.fsdecode(device),
                })

    def add_sensor(self, name, device, file):
        """Add a new sensor source. Use this to add non-iio illuminance sources"""
        new_id = len(self.sensors)
        self.sensors.append({
            'id': new_id,
            'name': name,
            'file': file,
            'device': device,
        })
        return new_id

    def get_luminance(self):
        """Get luminance from the active sensor"""
        with open(self.sensors[self.active]['file']) as file_in:
            return int(file_in.read().strip())

    def activate(self, sensor_id):
        """Include display in the used displays list"""
        self.active = sensor_id

    def get_active(self):
        """Get id of the active sensor"""
        return self.active
