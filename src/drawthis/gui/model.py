from drawthis import SettingsManager
from drawthis.app.signals import folder_added, widget_deleted, timer_changed

"""
Model to keep current State for Draw-This.

This module defines the Model and interface with persistence module.
It has two main classes:

- TkinterInterface:
    Manages app state (folders, timers, selected timer) and bridges
    between GUI, backend, and persistence (settings).

Usage
-----
This file is imported as a package according to the following:
     import gui.model
"""

class Model:
    """Manages app state and bridges GUI with backend and persistence layers.

        Attributes:
            :ivar folders (list[tuple[str, tk.BooleanVar]]): Folder paths with enabled flags.
            :ivar timers (list[int]): Available timers.
            :ivar selected_timer (int): Currently chosen timer duration.
        """

    def __init__(self):
        self._settings_manager = SettingsManager()
        self.last_session = self._settings_manager.read_config()
        self._folders: dict[str, bool] = {item.get("path",""): item.get("enabled", False) for item in self.last_session.get("folders","")}
        self._timers: list[int] = self.last_session.get("timers", [])
        self._selected_timer: int = self.last_session.get("selected_timer", 0)

        self._is_session_running = False

    #Public API:

    def add_timer(self, timer: int) -> None:
        """Add a new timer if not already present.

                Args:
                    :param timer: Duration in seconds.
                """

        self._timers.append(timer)
        self._timers = sorted(self._timers)
        timer_changed.send(self)

    def add_folder(self, folder_path: str) -> None:
        """Asks user for a folder and adds new folder if not already present.
                """

        self._folders[folder_path] = True
        folder_added.send(self, folder_path=folder_path)

    def delete_item(self, widget_type: str, value: str | int) -> None:
        """Removes a folder or timer from the attributes that store them.

                Args:
                    :param widget_type:
                    :param value: Folder or Timer to be deleted from internal list.
                """
        handlers = {
            "folder": lambda v: self._folders.pop(v),
            "timer": lambda v: self._timers.remove(v)
        }
        handlers.get(widget_type, lambda v: None)(value)
        widget_deleted.send(self, widget_type=widget_type, value=value)

    def set_folder_enabled(self, folder_path: str, enabled: bool) -> None:
        if folder_path not in self._folders:
            raise KeyError("Invalid folder")
        self._folders[folder_path] = enabled

    def save_session(self) -> None:
        """Sets all current parameters in the settings_manager and saves to config.json.
                """
        data = self.session_parameters
        self._settings_manager.write_config(data)
        self.last_session = data

    #Acessors:

    @property
    def folders(self) -> dict[str, bool]:
        """Returns a list[tuple[str,bool]] of all folders.
                """

        return self._folders.copy()

    @property
    def timers(self) -> list[int]:
        """Returns a list[int] of all internal timers.
                """

        return self._timers.copy()

    @property
    def selected_timer(self) -> int:
        """Returns the last used timer.
                """

        return self._selected_timer

    @selected_timer.setter
    def selected_timer(self, timer: int) -> None:
        """Sets internal attribute to a passes timer value.

                Args:
                    :param timer: Duration in seconds.
                """

        self._selected_timer = timer

    @property
    def is_session_running(self):

        return self._is_session_running

    @is_session_running.setter
    def is_session_running(self, value):

        self._is_session_running = value

    @property
    def session_parameters(self) -> dict:
        return {
            "folders": [{"path": folder_path, "enabled": enabled} for folder_path, enabled in
                        self.folders.items()],
            "timers": [timer for timer in self.timers],
            "selected_timer": self.selected_timer,
            "selected_folders_hash": hash(frozenset(path for path, enabled in self.folders.items() if enabled))
        }

    def should_recalculate(self) -> bool:
        """Returns a bool indicating whether selected folders has changed
        since the last slideshow.
                """

        selected_folders = hash(frozenset(path for path, enabled in self.folders.items() if enabled))
        if selected_folders != self.last_session.get("selected_folders_hash", ""):
            return True
        return False

