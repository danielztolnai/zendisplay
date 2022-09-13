"""Wrapper module for ddcutil"""
import subprocess
from displays import Display

class DisplayDDCUtil(Display):
    """Handle displays through ddcutil"""
    def __init__(self, name=None, path=None, bus=None):
        super().__init__(name, path)
        self.bus = bus
        self.brightness = None

    @classmethod
    def detect(cls, parameters=None):
        """Find all displays connected to the system"""
        try:
            output = cls.command("detect")
        except subprocess.CalledProcessError:
            print('ddcutil detect failed')
            return

        current_valid = False
        current_bus, current_name = (None, None)

        for line in output.splitlines():
            if len(line) == 0:
                pass
            elif not line[0].isspace():
                if line.startswith('Display'):
                    current_valid = True
                else:
                    current_valid = False
                    current_bus, current_name = (None, None)
            elif current_valid:
                line = line.strip()
                if line.startswith('I2C bus'):
                    current_bus = line.split("/dev/i2c-")[1].strip()
                elif line.startswith('Monitor:'):
                    current_name = line.split("Monitor:")[1].strip()

            if current_name is not None and current_bus is not None:
                yield cls(name=current_name, path="/dev/i2c-" + str(current_bus), bus=current_bus)
                current_bus, current_name = (None, None)

    @classmethod
    def command(cls, cmd):
        """Run a command through ddcutil"""
        command = ['ddcutil', "--brief"]
        try:
            cmd = cmd.split()
        except AttributeError:
            pass
        command += cmd

        output = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            check=True
        ).stdout.decode('utf-8').strip()

        return output

    def read_brightness(self):
        """Get brightness from the display"""
        try:
            data = self.command(['--bus', str(self.bus), 'getvcp', '0x10'])
            self.brightness = int(data.split()[3])
        except subprocess.CalledProcessError:
            self.brightness = None
            print('ddcutil getvcp failed')

    def get_brightness(self):
        """Return last brightness value"""
        if not self.enabled:
            return None

        if self.brightness is None:
            self.read_brightness()

        return self.brightness

    def _set_brightness(self, brightness):
        try:
            self.command(['--bus', str(self.bus), 'setvcp', '0x10', str(brightness)])
            self.brightness = brightness
        except subprocess.CalledProcessError:
            print('ddcutil setvcp failed')
