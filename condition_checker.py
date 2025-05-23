"""Run callbacks based on the result of condition evaluation"""
from typing import Callable
from zendisplay_config import Config
from condition_checker_xserver import ConditionCheckerXserver

class ConditionChecker():
    """Handle confition changes"""
    def __init__(
        self,
        cb_get: Callable[[], int],
        cb_set: Callable[[int], None],
        true_value=100,
        config='max_brightness',
    ):
        self.original_value = 0
        self.previous_condition = False
        self.true_value = true_value
        self.cb_get = cb_get
        self.cb_set = cb_set
        self.config_key = config
        self.checker = None

    def _init_condition_checkers(self):
        conditions = Config().get('conditions', self.config_key)
        if not bool(conditions):
            return None
        return ConditionCheckerXserver(conditions)

    def is_enabled(self) -> bool:
        """Return whether the condition is enabled"""
        return self.checker is not None

    def set_enabled(self, enabled=True):
        """Enable/disable the condition checker"""
        if not enabled:
            self.checker = None
            return
        if not self.is_enabled():
            self.checker = self._init_condition_checkers()

    def run(self):
        """Process condition changes"""
        if not self.is_enabled():
            return

        condition_check = self.checker.process()

        if (condition_check is None) or (condition_check == self.previous_condition):
            return
        self.previous_condition = condition_check

        if condition_check is True:
            self.original_value = self.cb_get()
            self.cb_set(self.true_value)
            print('condition check override start')

        if condition_check is False:
            self.cb_set(self.original_value)
            print('condition check override end')
