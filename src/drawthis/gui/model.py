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

class TkinterInterface:
    """Manages app state and bridges GUI with backend and persistence layers.

        Attributes:
            :ivar folders (list[tuple[str, tk.BooleanVar]]): Folder paths with enabled flags.
            :ivar timers (list[int]): Available timers.
            :ivar selected_timer (int): Currently chosen timer duration.
        """

    def __init__(self):
        self._settings_manager = sett.SettingsManager(folders={}, timers= [], last_timer= 0)
        self._folders: dict[str, bool] = {item[0]: item[1] for item in self._settings_manager.get_folders().items()}
        self._timers: list[int] = self._settings_manager.get_timers()
        self._selected_timer: int = self._settings_manager.get_last_timer()

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

        self._settings_manager.set_last_timer(self._selected_timer)
        self._settings_manager.set_timers(self._timers)
        self._settings_manager.set_folders(self.get_folders())
        self._settings_manager.write_config()


    #Acessors:

    def get_folders(self) -> dict[str, bool]:
        """Returns a list[tuple[str,bool]] of all folders.
                """

        return self._folders

    def get_selected_timer(self) -> int:
        """Returns the last used timer.
                """

        return self._selected_timer

    def get_timers(self) -> list[int]:
        """Returns a list[int] of all internal timers.
                """

        return self._timers

    def set_selected_timer(self, timer: int) -> None:
        """Sets internal attribute to a passes timer value.

                Args:
                    :param timer: Duration in seconds.
                """

        self._selected_timer = timer

    def get_current_state(self):

        current_state = {
            "folders": [item[0] for item in self.get_folders().items() if item[1]],
            "timer": self.get_selected_timer(),
            "recalculate": self._should_recalculate()
        }
        return current_state


    #Private helpers:

    def _should_recalculate(self) -> bool:
        """Returns a bool indicating whether selected folders has changed
        since the last slideshow.
                """

        selected_folders = {item[0] for item in self.get_folders().items() if item[1]}
        previous_folders = {item[0] for item in self._settings_manager.get_folders().items() if item[1]}
        if selected_folders != previous_folders:
            return True
        return False


