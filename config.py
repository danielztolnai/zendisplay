"""Module to manage configuration files"""
import os
from configparser import ConfigParser, _UNSET, Error # type: ignore[attr-defined]

class NoDefaultError(Error):
    """Raised when no default is present for the given option"""
    def __init__(self, option, section):
        super().__init__(f'No default set for option {option} in section: {section}')


# pylint: disable-next=too-many-ancestors
class Config(ConfigParser):
    """Manage configuration files"""
    _instance = None
    _original_instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = cls._get_new_instance(*args, **kwargs)
        return cls._instance

    def __init__(self, initialize=False):
        if initialize is True:
            super().__init__()
            self.read(self._get_config_file_paths())

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
        config_changes = self._changes()
        if config_changes is None:
            return

        path = self._get_config_file_paths()[-1]
        try:
            if not os.path.exists(os.path.dirname(path)):
                os.mkdir(os.path.dirname(path), mode=0o755)
            with open(path, 'w', encoding='utf-8') as config_file:
                config_changes.write(config_file)
            self._original().read_dict(config_changes)
        except (FileNotFoundError, OSError) as exception:
            print(f'Could not save configuration: {exception}')

    def _changes(self):
        changes = {}
        for section_name, section in self.items():
            for option, value in section.items():
                if self._original().get(section_name, option) == value:
                    continue
                if section_name not in changes:
                    changes[section_name] = {}
                changes[section_name][option] = value

        if not bool(changes):
            return None

        config_changes = ConfigParser()
        config_changes.read_dict(changes)
        return config_changes

    @classmethod
    def _get_new_instance(cls, *args, **kwargs):
        instance = object.__new__(cls, *args, **kwargs)
        instance.__init__(initialize=True)
        return instance

    @classmethod
    def _get_config_file_paths(cls):
        dirname = os.path.dirname(os.path.abspath(__file__))
        return (
            os.path.join(dirname, f'{cls._config_name()}.conf.example'),
            os.path.join(dirname, f'{cls._config_name()}.conf'),
            os.path.join(
                os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config')),
                cls._config_name(),
                f'{cls._config_name()}.conf'
            ),
        )

    @classmethod
    def _original(cls):
        if not isinstance(cls._original_instance, cls):
            cls._original_instance = cls._get_new_instance()
        return cls._original_instance

    @staticmethod
    def _config_name():
        """Returns the name of the application"""
        raise NotImplementedError()

    @staticmethod
    def _config_defaults():
        """Returns every option and their default values in a dict"""
        raise NotImplementedError()
