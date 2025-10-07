from drawthis.core.constants import DATABASE_FILE
from drawthis.core.models.state import Session

from drawthis.core.events.bus import (
    widget_deleted,
    timer_changed,
    folder_added,
)
from drawthis.persistence.settings.json_persistence import SettingsManager
from drawthis.services.session.db_service import DatabaseManager

"""
Model to keep session state for Draw-This.

This module defines the Model and interface with persistence module.
It has two main classes:

- Model:
    Manages app state (folders, timers, etc) and persistence (settings).

Usage
-----
This file is imported by Viewmodel as a package according to the following:
     from drawthis import Model
"""


class Model:
    """Manages app state and bridges GUI with backend and persistence layers.

    Do NOT mutate session from outside the model.
    Attributes:
        :ivar folders (list[tuple[str, tk.BooleanVar]]):
        :ivar timers (list[int]):
        :ivar selected_timer (int): Currently chosen timer duration.
    """

    def __init__(self):
        self._settings_manager = SettingsManager()
        self._database_manager = DatabaseManager(DATABASE_FILE)
        self.session = Session()
        self.last_session = Session()

    # Public API

    def load_last_session(self):
        """Explicitly load previous session from settings."""
        self.last_session = self._settings_manager.read_config()
        self.session = self.last_session.copy()  # or maybe a copy

    def add_timer(self, timer: int) -> None:
        """
        Add timer to session

        The timer with value 0 is internally the indefinite, default timer,
        and must not be added with add_timer

        Raises:
            ValueError: timers must be positive, non-zero integers
        """
        if timer <= 0:
            raise ValueError(f"Invalid timer inserted: {timer}")
        self.session.timers.add(timer)
        timer_changed.send(self)

    def add_folder(self, folder: str) -> None:
        """Add folder to session"""
        self.session.folders.add(folder)
        folder_added.send(self, folder_path=folder)

    def delete_folder(self, path: str) -> None:
        """Delete folder from session."""
        self.session.folders.remove(path)
        widget_deleted.send(self, widget_type="folder", value=path)

    def set_selected_timer(self, timer: int) -> None:
        """Set the selected timer"""
        self.session.selected_timer = timer

    def delete_timer(self, timer: int) -> None:
        """Delete timer from session."""
        self.session.timers.remove(timer)
        widget_deleted.send(self, widget_type="timer", value=timer)

    def save_session(self) -> None:
        """Set session parameters in settings_manager and persists"""
        self._settings_manager.write_config(self.session.copy())
        self.last_session = self.session.copy()

    # Acessors:

    @property
    def session_is_running(self) -> bool:
        """Add a new timer if not already present."""
        return self.session.is_running

    @session_is_running.setter
    def session_is_running(self, value: bool) -> None:
        """Add a new timer if not already present."""
        self.session.is_running = value

    def recalculate_if_should_recalculate(self) -> None:
        """
        Recalculates database if folders changed from last session.
        Deleted folders are disabled folders or removed folders.
        """
        current_folders = set(self.session.folders.enabled)
        if not current_folders:
            return
        previous_folders = set(self.last_session.folders.enabled)
        if current_folders == previous_folders:
            return
        added_folders = current_folders - previous_folders
        deleted_folders = previous_folders - current_folders
        if deleted_folders:
            self._database_manager.remove_rows(deleted_folders)
        if added_folders:
            self._database_manager.add_rows(added_folders)
