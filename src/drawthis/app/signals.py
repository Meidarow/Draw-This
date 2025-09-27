from blinker import Namespace

app_signals = Namespace()

# Model → ViewModel → View communication
folder_added = app_signals.signal("folder-added")
timer_changed = app_signals.signal("timer-changed")
widget_deleted = app_signals.signal("widget-deleted")
session_running = app_signals.signal("session-running")
session_ended = app_signals.signal("session-ended")