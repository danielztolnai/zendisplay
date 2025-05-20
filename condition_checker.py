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
        self.checker = self._init_condition_checkers(config)

    @staticmethod
    def _init_condition_checkers(config: str):
        conditions = Config().get('conditions', config)
        if not bool(conditions):
            return None
        return ConditionCheckerXserver(conditions)

    def set_true_value(self, value: int):
        """Change the value to set when the conditions are fulfilled"""
        self.true_value = value

    def run(self):
        """Process condition changes"""
        if self.checker is None:
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
