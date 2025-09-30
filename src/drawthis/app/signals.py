from blinker import Namespace
"""
This module defines all signals used in the app, created in the app_signals Namespace

Usage
-----
This file is imported by Viewmodel as a package according to the following:
    from drawthis import signals
"""
app_signals = Namespace()


folder_added = app_signals.signal("folder-added")
timer_changed = app_signals.signal("timer-changed")
widget_deleted = app_signals.signal("widget-deleted")
session_started = app_signals.signal("session-started")
session_ended = app_signals.signal("session-ended")