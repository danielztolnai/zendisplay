"""Condition checker for the X.org server"""
from typing import List
from contextlib import contextmanager
from Xlib.display import Display
from Xlib.error import XError
from Xlib.X import AnyPropertyType, PropertyChangeMask, PropertyNotify
from Xlib.xobject.drawable import Window

class ConditionCheckerXserver():
    """Evaluate condition changes on the X server"""
    def __init__(self, conditions: str):
        self.display = Display()
        self.root = self.display.screen().root
        self.atoms = {
            '_NET_ACTIVE_WINDOW': self.display.intern_atom('_NET_ACTIVE_WINDOW'),
            '_NET_WM_STATE': self.display.intern_atom('_NET_WM_STATE'),
        }
        self.root.change_attributes(event_mask=PropertyChangeMask)
        self.current_window_id = None
        self.conditions = self._parse_conditions(conditions)

    def _parse_conditions(self, conditions: str) -> list:
        data: List[tuple] = []
        if not bool(conditions):
            return data
        for condition in conditions.split('|'):
            data.append(tuple(self.display.intern_atom(item) for item in condition.split('=', 1)))
        return data

    @staticmethod
    def _has_value(data) -> bool:
        return (
            bool(data) and hasattr(data, 'value')
            and bool(data.value) and hasattr(data.value, '__getitem__')
        )

    @contextmanager
    def current_window(self) -> Window:
        """Get the currently active window"""
        window = None
        try:
            result = self.root.get_full_property(self.atoms['_NET_ACTIVE_WINDOW'], AnyPropertyType)
            if self._has_value(result):
                window = self.display.create_resource_object('window', result.value[0])
        except XError:
            pass
        yield window

    def _check_condition(self, window: Window, condition: tuple) -> bool:
        try:
            result = window.get_full_property(condition[0], AnyPropertyType)
            if result is None:
                return False
            if len(condition) < 2:
                return True
            return self._has_value(result) and (condition[1] in result.value)
        except XError:
            return False

    def _check_conditions(self, window) -> bool:
        for condition in self.conditions:
            if self._check_condition(window, condition) is False:
                return False
        return True

    def _has_window_changed_event(self) -> bool:
        event = self.display.next_event()
        return (
            event and hasattr(event, 'type') and hasattr(event, 'atom')
            and (event.type == PropertyNotify)
            and (event.atom == self.atoms['_NET_ACTIVE_WINDOW'])
        )

    def _is_window_changed(self) -> bool:
        result = False
        number_of_events = self.display.pending_events()
        while number_of_events > 0:
            if self._has_window_changed_event():
                result = True
            number_of_events -= 1
        return result

    def _get_filter_change(self):
        with self.current_window() as window:
            if window is None or (window.id == self.current_window_id):
                return None
            self.current_window_id = window.id

            return self._check_conditions(window)

    def process(self):
        """Process condition changes"""
        if not self._is_window_changed():
            return None

        return self._get_filter_change()
