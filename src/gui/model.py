import tkinter as tk
import pathlib as path
from launcher.feh_backend import start_slideshow
import settings.settings_manager as sett
from utils.filedialogs import select_file


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
        self.settings_manager = sett.SettingsManager(folders=[], timers= [], last_timer= 0)
        self.folders = [(folder,tk.BooleanVar(value=enabled)) for folder, enabled in self.settings_manager.get_folders()]
        self.timers = self.settings_manager.get_timers()
        self.selected_timer = self.settings_manager.get_last_timer()
        self.start_folder = "/mnt/Storage/Art/Resources"
        self.database_folder = path.Path("~/.config/draw-this/image_paths.db").expanduser()


    #Public API:

    def add_custom_timer(self, custom_timer: tk.Entry) -> None:
        """Add a new timer selected by the user if field not empty.

                Args:
                    :param custom_timer: Duration in seconds selected by the user.
                """

        if custom_timer.get() == "":
            return

        self.add_timer(int(custom_timer.get()))

    def add_timer(self, timer: int) -> None:
        """Add a new timer if not already present.

                Args:
                    :param timer: Duration in seconds.
                """

        if timer in self.timers or timer == 0:
            return

        self.timers.append(timer)
        self.timers = sorted(self.timers)

    def add_folder(self) -> tuple[str, tk.BooleanVar]:
        """Asks user for a folder and adds new folder if not already present.
                """

        folder_path = select_file(root=self.start_folder)
        if not folder_path or folder_path in [f for f, _ in self.folders]:
            return "", tk.BooleanVar(value=False)

        var = tk.BooleanVar(value=True)
        self.folders.append((folder_path, var))
        return folder_path, var

    def delete_item(self, value: str | int) -> None:
        """Removes a folder or timer from the attributes that store them.

                Args:
                    :param value: Folder or Timer to be deleted from internal list.
                """
        if isinstance(value, str):
            self.folders = [t for t in self.folders if t[0] != value]
            return

        if isinstance(value, int):
            self.timers.remove(value)
            return

    def start_slideshow(self, timer: tk.IntVar) -> None:
        """Passes GUI state to feh backend to start slideshow.

                Args:
                    :param timer: Slideshow duration in seconds.
                """

        self.set_selected_timer(timer.get())
        selected_folders = [folder for folder, enabled in self.get_folders() if enabled]
        if not selected_folders:
            return
        recalculate = self._should_recalculate()
        start_slideshow(selected_folders, geometry=None, drawing_time=self.selected_timer,
                        db_path=self.database_folder, recalculate=recalculate)
        self._save_session()


    #Acessors:

    def get_folders(self) -> list[tuple[str, bool]]:
        """Returns a list[tuple[str,bool]] of all folders.
                """

        return [(folder, tk_enabled.get()) for (folder, tk_enabled) in self.folders]

    def get_tk_folders(self) -> list[tuple[str,tk.BooleanVar]]:
        """Returns a list[tuple[str,tk.BooleanVar]] of all folders.
                """

        return self.folders

    def get_last_timer(self) -> int:
        """Returns the last used timer.
                """

        return self.selected_timer

    def get_timers(self) -> list[int]:
        """Returns a list[int] of all internal timers.
                """

        return self.timers

    def set_selected_timer(self, timer: int) -> None:
        """Sets internal attribute to a passes timer value.

                Args:
                    :param timer: Duration in seconds.
                """

        self.selected_timer = timer

    #Private helpers:

    def _should_recalculate(self) -> bool:
        """Returns a bool indicating whether selected folders has changed
        since the last slideshow.
                """

        selected_folders = [folder for folder, enabled in self.get_folders() if enabled]
        previous_folders = [folder for folder, enabled in self.settings_manager.get_folders() if enabled]
        if selected_folders != previous_folders:
            return True
        return False

    def _save_session(self) -> None:
        """Sets all current parameters in the settings_manager and saves to config.json.
                """

        self.settings_manager.set_last_timer(self.selected_timer)
        self.settings_manager.set_timers(self.timers)
        self.settings_manager.set_folders(self.get_folders())
        self.settings_manager.write_config()

