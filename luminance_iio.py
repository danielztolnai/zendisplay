"""Get ambient lighting from IIO bus compatible sensors"""
import os
from base_classes import LuminanceSource

class LuminanceIIO(LuminanceSource):
    """Handle ambient lighting sensors through sysfs"""
    SYSFS_IIO_PATH = '/sys/bus/iio/devices/'
    SYSFS_IIO_ILLUMINANCE_FILE = 'in_illuminance_raw'
    SYSFS_IIO_NAME_FILE = 'name'

    def __init__(self, name=None, path=None, file=None):
        super().__init__(name, path)
        self._set_ready(True)
        self.file = file

    @classmethod
    def detect(cls, parameters=None):
        """Find all sensors connected to the system"""
        directory = os.fsencode(cls.SYSFS_IIO_PATH)
        if not os.path.isdir(directory):
            return

        for device in os.listdir(directory):
            device_path = os.path.join(cls.SYSFS_IIO_PATH, os.fsdecode(device))
            # Check if device is an illuminance sensor
            if not os.path.isfile(os.path.join(device_path, cls.SYSFS_IIO_ILLUMINANCE_FILE)):
                continue
            # Get name and add to list
            name_file_path = os.path.join(device_path, cls.SYSFS_IIO_NAME_FILE)
            with open(name_file_path, encoding='utf-8') as file_in:
                device_name = file_in.read().strip()
                device_file = os.path.join(device_path, cls.SYSFS_IIO_ILLUMINANCE_FILE)
                yield cls(name=device_name, path=os.fsdecode(device), file=device_file)

    def get_luminance(self):
        """Get luminance from the sensor"""
        with open(self.file, encoding='utf-8') as file_in:
            return int(file_in.read().strip())
