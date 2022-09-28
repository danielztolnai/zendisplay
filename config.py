"""Module to manage configuration files"""
import os
from configparser import ConfigParser, _UNSET, Error

class NoDefaultError(Error):
    """Raised when no default is present for the given option"""
    def __init__(self, option, section):
        super().__init__(f'No default set for option {option} in section: {section}')


# pylint: disable-next=too-many-ancestors
class Config(ConfigParser):
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

    # pylint: disable-next=unused-argument
    def get(self, section, option, *args, fallback=_UNSET, **kwargs):
        default_value = self._config_defaults().get(section, {}).get(option, _UNSET)

        if default_value is _UNSET:
            raise NoDefaultError(option, section)

        if not bool(kwargs):
            if isinstance(default_value, bool):
                return self.getboolean(section, option, fallback=default_value)
            if isinstance(default_value, int):
                return self.getint(section, option, fallback=default_value)
            if isinstance(default_value, float):
                return self.getfloat(section, option, fallback=default_value)

        return super().get(section, option, *args, fallback=default_value, **kwargs)

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


    @staticmethod
    def _config_name():
        """Returns the name of the application"""
        raise NotImplementedError()

    @staticmethod
    def _config_defaults():
        """Returns every option and their default values in a dict"""
        raise NotImplementedError()
