#!/usr/bin/env python3
"""Small script to adjust display brightness according to ambient lighting"""
import os
from zendisplay_config import Config

def _get_gui_type():
    """Detect the GUI type to use"""
    config = Config().get('general', 'gui')
    if config in ('gtk', 'qt'):
        return config
    if os.environ.get("DESKTOP_SESSION") in ("ubuntu", "cinnamon"):
        return 'gtk'
    return 'qt'

if _get_gui_type() == 'gtk':
    from zendisplay_gtk import ZenDisplay
else:
    from zendisplay_qt import ZenDisplay

ZenDisplay().run()
