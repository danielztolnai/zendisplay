"""Wrapper module for ddcutil"""
class Displays:
    """Handle displays through ddcutil"""
    def __init__(self):
        self.iter_id = 0
        self.displays = []
        self.detect()
        self.read_brightness()

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

    @classmethod
    def command(cls, cmd):
        """Run a command through ddcutil"""
        import subprocess
        command = ['ddcutil', "--brief", "--nodetect"]
        try:
            cmd = cmd.split()
        except AttributeError:
            pass
        command += cmd
        output = subprocess.run(command, stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
        return output

    def detect(self):
        """Find all displays connected to the system"""
        output = self.command("detect")

        for line in output.splitlines():
            line = line.strip()
            if line.startswith('Display'):
                self.displays.append({'id': len(self.displays), 'use': True})
            elif line.startswith('I2C bus'):
                self.displays[-1]['bus'] = line.split("/dev/i2c-")[1].strip()
            elif line.startswith('Monitor:'):
                self.displays[-1]['name'] = line.split("Monitor:")[1].strip()

    def read_brightness(self):
        """Get brightness from displays"""
        for display in self.displays:
            data = self.command(['--bus', str(display['bus']), 'getvcp', '0x10'])
            display['brightness'] = int(data.split()[3])

    def get_brightness(self):
        """Return last brightness value"""
        for display in self.displays:
            if display['use'] is True:
                return display['brightness']
        return None

    def set_brightness(self, brightness):
        """Set brightness for displays"""
        if brightness == self.get_brightness():
            return
        if brightness > 100 or brightness < 0:
            return

        for display in self.displays:
            if display['use'] is True:
                self.command(['--bus', str(display['bus']), 'setvcp', '0x10', str(brightness)])
                display['brightness'] = brightness

    def set_active(self, display_id, active):
        """Include/exclude display in the used displays list"""
        self.displays[display_id]['use'] = bool(active)
