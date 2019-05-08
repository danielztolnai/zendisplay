"""Get ambient lighting from IIO bus compatible sensors"""
from luminance_sources import LuminanceSource

class LuminanceIIO(LuminanceSource):
    """Handle ambient lighting sensors through sysfs"""
    SYSFS_IIO_PATH = '/sys/bus/iio/devices/'
    SYSFS_IIO_ILLUMINANCE_FILE = 'in_illuminance_raw'
    SYSFS_IIO_NAME_FILE = 'name'

    def __init__(self, name=None, path=None, file=None):
        super().__init__(name, path)
        self.file = file

    @classmethod
    def detect(cls, parameters=None):
        """Find all sensors connected to the system"""
        import os
        directory = os.fsencode(cls.SYSFS_IIO_PATH)
        for device in os.listdir(directory):
            device_path = os.path.join(cls.SYSFS_IIO_PATH, os.fsdecode(device))
            # Check if device is an illuminance sensor
            if not os.path.isfile(os.path.join(device_path, cls.SYSFS_IIO_ILLUMINANCE_FILE)):
                continue
            # Get name and add to list
            with open(os.path.join(device_path, cls.SYSFS_IIO_NAME_FILE)) as file_in:
                device_name = file_in.read().strip()
                device_file = os.path.join(device_path, cls.SYSFS_IIO_ILLUMINANCE_FILE)
                yield cls(name=device_name, path=os.fsdecode(device), file=device_file)

    def get_luminance(self):
        """Get luminance from the sensor"""
        with open(self.file) as file_in:
            return int(file_in.read().strip())
