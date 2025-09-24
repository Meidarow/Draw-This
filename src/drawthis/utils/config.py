import pathlib as path
import json


"""
Persistence manager for Draw-This.

This module defines the settings manager and its interface with a JSON file used for persistence.
It has a single class:

- SettingsManager:
    Manages persistence of app state (folders, timers, selected timer) across multiple runs
    and can store previous session parameters in a JSON file in ~/.config/.

Usage
-----
This file is imported as a package according to the following:
    import settings.settings_manager
"""

class SettingsManager:
    """Manages app state and bridges GUI with backend and persistence layers.

        Attributes:
            :ivar folders (list[tuple[str, tk.BooleanVar]]): Folder paths with enabled flags from previous session.
            :ivar timers (list[int]): Previously available timers.
            :ivar last_timer (int): Previously chosen timer duration.
        """

    def __init__(self, folders: dict[str, bool], timers: list[int], last_timer: int):
        self.folders = folders
        self.timers = timers
        self.last_timer = last_timer

        config_path = path.Path("~/.config/draw-this").expanduser()
        config_path.mkdir(parents=True, exist_ok=True)
        self.config_file = config_path / "draw-this.json"
        self.read_config()

    # Public API:

    def read_config(self):
        """Parses file and restores previous session's final values to internal attributes.
                """
        if not self.config_file.exists():
            self.config_file.touch()

        try:
            with open(self.config_file, "r", encoding='utf-8') as config:
                read_data = json.load(config)
        except (json.JSONDecodeError, FileNotFoundError):
            read_data = {"folders": [], "timers": [], "last_timer": 0}

        self.folders = {item.get("path",""): item.get("enabled", False) for item in read_data.get("folders", [])}
        self.timers = read_data.get("timers", [])
        self.last_timer = read_data.get("last_timer", 0)

    def write_config(self):
        """Creates file and stores the current session's values from internal attributes.
                """
        data = {
            "folders": [{"path": folder_path, "enabled": enabled} for folder_path, enabled in self.folders.items()],
            "timers": [timer for timer in self.timers],
            "last_timer": self.last_timer
        }
        with open(file=self.config_file, mode='w', encoding='utf-8') as config:
            json.dump(obj=data, fp=config, indent=4)

    # Accessors:

    def get_folders(self):
        """Returns folder list from internal attributes.
                """
        return self.folders

    def set_folders(self, folders: dict):
        """Updates folder list in internal attributes.

                Args:
                    :param folders: List of tuples containing folder path and boolean showing enabled status
                """
        if folders != self.folders:
            self.folders = folders

    def get_last_timer(self):
        """Returns last used timer from internal attributes.
                """
        return self.last_timer

    def set_last_timer(self, last_timer: int):
        """Updates last used timer in internal attributes.

                Args:
                    :param last_timer: Duration in seconds
                """
        self.last_timer = last_timer

    def get_timers(self):
        """Returns timer list from internal attributes.
                """
        return self.timers

    def set_timers(self, timers: list[int]):
        """updates timer list in internal attributes.

                Args:
                    :param timers: List of durations in seconds
                """
        if timers != self.timers:
            self.timers = timers
            self.timers = sorted(self.timers)
