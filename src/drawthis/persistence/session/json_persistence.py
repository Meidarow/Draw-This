import json
import pathlib as path

from drawthis.core.models.session.dataclasses import Session

"""
Persistence manager for Draw-This.

This module defines the settings manager and its interface with a JSON file
used for persistence.
It has a single class:

- SettingsManager:
Manages persistence of app state (folders, timers, selected timer) across
multiple runs
and can store previous session parameters in a JSON file in ~/.config/.

Usage
-----
This file is imported as a package according to the following:
    import settings.settings_manager
"""


# TODO
class SessionJSONPersistence:
    """Manages app state and bridges GUI with backend and persistence layers.

    Attributes:
        :ivar folders (list[tuple]): Folder paths with enabled flags from
        previous session.
        :ivar timers (list[int]): Previously available timers.
        :ivar selected_timer (int): Previously chosen timer duration.
    """

    def __init__(self):
        config_path = path.Path("~/.config/draw-this").expanduser()
        config_path.mkdir(parents=True, exist_ok=True)
        self.config_file = config_path / "draw-this.json"

    # Public API:

    def read_config(self) -> Session:
        """Parse file and restores previous session's final values."""
        if not self.config_file.exists():
            self.config_file.touch()
        try:
            with open(self.config_file, "r", encoding="utf-8") as config:
                read_data = json.load(config)
        except (json.JSONDecodeError, FileNotFoundError):
            read_data = {"folders": {}, "timers": [], "selected_timer": 0}

        return Session.from_dict(read_data)

    def write_config(self, session: Session) -> None:
        """Create file and stores the current session's values."""
        try:
            with open(
                file=self.config_file, mode="w", encoding="utf-8"
            ) as config:
                json.dump(obj=session.to_dict(), fp=config, indent=4)
        except FileNotFoundError:
            return
