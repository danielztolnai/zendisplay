"""Configuration for Zendisplay"""
from config import Config as ConfigBase

class Config(ConfigBase):
    """Manage configuration files"""
    @staticmethod
    def _config_name():
        return 'zendisplay'

    @staticmethod
    def _config_defaults():
        return {
            'general': {
                'default_sensor': 0,
                'show_notifications': False,
                'gui': 'default',
            },
            'brightness': {
                'increment': 5,
                'margin': 5,
                'slope': 0.2,
                'base_value': 0,
            },
            'mqtt': {
                'subscribe': False,
                'publish': False,
                'host': 'mqtt.example.com',
                'topic': 'zendisplay/brightness',
            },
            'conditions': {
                'enabled': False,
                'max_brightness': '',
            },
        }
