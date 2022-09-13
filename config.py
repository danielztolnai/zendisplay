"""Module to manage configuration files"""
import os
import configparser

class Config(configparser.ConfigParser): # pylint: disable=too-many-ancestors
    """Manage configuration files"""
    _instance = None
    _initialized = False
    _name = 'zendisplay'

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        super().__init__()
        self._load_config_file()
        self._initialized = True

    @classmethod
    def _get_config_file_paths(cls):
        """Generate config path priority list"""
        return (
            os.path.join(
                os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config')),
                cls._name,
                f'{cls._name}.conf'
            ),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), f'{cls._name}.conf'),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), f'{cls._name}.conf.example'),
        )

    def _load_config_file(self):
        """Read first available configuration file"""
        for path in self._get_config_file_paths():
            if os.path.isfile(path):
                self.read(path)
                return

    def save(self):
        """Write current data to configuration file"""
        path = self._get_config_file_paths()[0]
        try:
            if not os.path.exists(os.path.dirname(path)):
                os.mkdir(os.path.dirname(path), mode=0o755)
            with open(path, 'w', encoding='utf-8') as config_file:
                self.write(config_file)
        except (FileNotFoundError, OSError) as exception:
            print(f'Could not save configuration: {exception}')
