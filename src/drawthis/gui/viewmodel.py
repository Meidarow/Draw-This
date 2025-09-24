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

class TkinterViewmodel:
    """Manages app state and bridges GUI with backend and persistence layers.

        Attributes:
            :ivar folders (list[tuple[str, tk.BooleanVar]]): Folder paths with enabled flags.
            :ivar timers (list[int]): Available timers.
            :ivar selected_timer (int): Currently chosen timer duration.
        """

    def __init__(self, last_session):
        self._folders: dict[str, bool] = {item.get("path",""): item.get("enabled", False) for item in last_session.get("folders","")}
        self._timers: list[int] = last_session.get("timers", [])
        self._selected_timer: int = last_session.get("selected_timer", 0)

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
    def dump_state(self) -> dict:
        return {
            "folders": [{"path": folder_path, "enabled": enabled} for folder_path, enabled in
                        self.folders.items()],
            "timers": [timer for timer in self.timers],
            "selected_timer": self.selected_timer
        }

    def set_folder_enabled(self, folder_path: str, enabled: bool) -> None:
        if folder_path not in self._folders:
            raise KeyError("Invalid folder")
        self._folders[folder_path] = enabled