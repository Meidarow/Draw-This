import drawthis.utils.config as sett


"""
Model to keep current State for Draw-This.

This module defines the Model and interface with with persistence module.
It has two main classes:

- TkinterInterface:
    Manages app state (folders, timers, selected timer) and bridges
    between GUI, backend, and persistence (settings).

Usage
-----
This file is imported as a package according to the following:
     import gui.model
"""

class TkinterViewmodel:
    """Manages app state and bridges GUI with backend and persistence layers.

        Attributes:
            :ivar folders (list[tuple[str, tk.BooleanVar]]): Folder paths with enabled flags.
            :ivar timers (list[int]): Available timers.
            :ivar selected_timer (int): Currently chosen timer duration.
        """

    def __init__(self):
        self._settings_manager = sett.SettingsManager()
        self._last_session = self._settings_manager.read_config()
        self._folders: dict[str, bool] = {item.get("path",""): item.get("enabled", False) for item in self._last_session.get("folders","")}
        self._timers: list[int] = self._last_session.get("timers", [])
        self._selected_timer: int = self._last_session.get("timer", 0)

    #Public API:

    def add_timer(self, timer: int) -> None:
        """Add a new timer if not already present.

                Args:
                    :param timer: Duration in seconds.
                """

        self._timers.append(timer)
        self._timers = sorted(self._timers)

    def add_folder(self, folder_path: str) -> None:
        """Asks user for a folder and adds new folder if not already present.
                """

        self._folders[folder_path] = True

    def delete_item(self, value: str | int) -> None:
        """Removes a folder or timer from the attributes that store them.

                Args:
                    :param value: Folder or Timer to be deleted from internal list.
                """
        if isinstance(value, str):
            self._folders.pop(value)
            return

        if isinstance(value, int):
            self._timers.remove(value)
            return

    def save_session(self) -> None:
        """Sets all current parameters in the settings_manager and saves to config.json.
                """
        data = {
            "folders": [{"path": folder_path, "enabled": enabled} for folder_path, enabled in self._folders.items()],
            "timers": [timer for timer in self._timers],
            "last_timer": self._selected_timer
        }
        self._settings_manager.write_config(data)


    #Acessors:

    @property
    def folders(self) -> dict[str, bool]:
        """Returns a list[tuple[str,bool]] of all folders.
                """

        return self._folders.copy()

    @property
    def selected_timer(self) -> int:
        """Returns the last used timer.
                """

        return self._selected_timer

    @property
    def timers(self) -> list[int]:
        """Returns a list[int] of all internal timers.
                """

        return self._timers.copy()

    @selected_timer.setter
    def selected_timer(self, timer: int) -> None:
        """Sets internal attribute to a passes timer value.

                Args:
                    :param timer: Duration in seconds.
                """

        self._selected_timer = timer

    @property
    def current_state(self):

        current_state = {
            "folders": [path for path, enabled in self.folders.items() if enabled],
            "timer": self.selected_timer,
            "recalculate": self._should_recalculate()
        }
        return current_state


    #Private helpers:

    def _should_recalculate(self) -> bool:
        """Returns a bool indicating whether selected folders has changed
        since the last slideshow.
                """

        selected_folders = {path for path, enabled in self.folders.items() if enabled}
        previous_folders = {item.get("path") for item in self._last_session.get("folders") if item.get("enabled") }
        if selected_folders != previous_folders:
            return True
        return False


