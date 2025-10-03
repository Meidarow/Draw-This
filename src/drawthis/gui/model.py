from dataclasses import dataclass, field

from drawthis.app.config import SettingsManager
from drawthis.app.signals import widget_deleted, timer_changed, folder_added

"""
Model to keep current state for Draw-This.

This module defines the Model and interface with persistence module.
It has two main classes:

- Model:
    Manages app state (folders, timers, etc) and persistence (settings).

Usage
-----
This file is imported by Viewmodel as a package according to the following:
     from drawthis import Model
"""


@dataclass
class FolderSet:
    _folders: dict[str, bool] = field(default_factory=dict)

    @classmethod
    def from_pairs(cls, pairs: list[tuple[str, bool]]) -> "FolderSet":
        """Factory for FolderSet, from (path, enabled) pairs"""
        fs = cls()
        for path, enabled in pairs:
            fs.add(path, enabled)
        return fs

    def add(self, path: str, enabled: bool = True) -> None:
        """Add a folder with optional enabled state."""
        self._folders[path] = enabled

    def remove(self, path: str) -> None:
        """Remove a folder."""
        self._folders.pop(path, None)

    def toggle(self, path: str) -> None:
        """Flip enabled/disabled state for a folder."""
        if path in self._folders:
            self._folders[path] = not self._folders[path]

    def enable(self, path: str) -> None:
        """Enable a folder explicitly."""
        self._folders[path] = True

    def disable(self, path: str) -> None:
        """Disable a folder explicitly."""
        self._folders[path] = False

    def enabled(self) -> list[str]:
        """Return only enabled folders."""
        return [f for f, e in self._folders.items() if e]

    def disabled(self) -> list[str]:
        """Return only disabled folders."""
        return [f for f, e in self._folders.items() if not e]

    def all(self) -> dict[str, bool]:
        """Raw view of all folders and states."""
        return dict(self._folders)

    def copy(self) -> "FolderSet":
        """Return identical copy of self"""
        return FolderSet(_folders=self.all())


@dataclass
class TimerSet:
    _timers: list[int] = field(default_factory=list)

    @classmethod
    def from_list(cls, timers: list[int]) -> "TimerSet":
        """Factory for TimerSet from list of timers"""
        ts = cls()
        for timer in timers:
            ts.add(timer)
        return ts

    def add(self, timer: int) -> None:
        """Add a new timer if not already present. Sorts timer list"""
        self._timers.append(timer)
        self._timers = sorted(self._timers)

    def remove(self, timer: int) -> None:
        """Remove a timer"""
        self._timers.remove(timer)

    def all(self) -> list[int]:
        """Raw view of all timers"""
        return list(self._timers)

    def copy(self) -> "TimerSet":
        """Return identical copy of self"""
        return TimerSet(_timers=self.all())


@dataclass
class Session:
    timers: TimerSet = field(default_factory=TimerSet)
    folders: FolderSet = field(default_factory=FolderSet)
    selected_timer: int = None
    geometry: tuple = None
    is_running: bool = False

    @classmethod
    def from_dict(cls, session_dict: dict) -> "Session":
        sess = cls()
        sess.timers.from_list(session_dict.get("timers", []))
        sess.folders.from_pairs(session_dict.get("folders", []))
        sess.selected_timer = session_dict.get("selected_timer", 0)
        return sess

    def to_dict(self) -> dict:
        session_dict = {
            "timers": self.timers.all(),
            "folders": self.folders.all(),
            "selected_timer": self.selected_timer,
        }
        return session_dict

    def copy(self) -> "Session":
        return Session(
            timers=self.timers.copy(),
            folders=self.folders.copy(),
            selected_timer=self.selected_timer,
        )


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
        self.session = self.last_session = self._settings_manager.read_config()

    # Public API:

    def add_timer(self, timer: int) -> None:
        """Add timer to session"""
        self.session.timers.add(timer)
        timer_changed.send(self)

    def add_folder(self, folder: str) -> None:
        """Add folder to session"""
        self.session.folders.add(folder)
        folder_added.send(self)

    def delete_folder(self, path: str) -> None:
        """Delete folder from session."""
        self.session.folders.remove(path)
        widget_deleted.send(self, widget_type="folder", value=path)

    def delete_timer(self, timer: int) -> None:
        """Delete timer from session."""
        self.session.timers.remove(timer)
        widget_deleted.sent(self, widget_type="timer", value=timer)

    def save_session(self) -> None:
        """Set session parameters in settings_manager and persists"""
        self._settings_manager.write_config(self.session)
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
        """Recalculates database if folders changed from last session."""
        previous_folders = self.last_session.folders.enabled()
        selected_folders = self.session.folders.enabled()
        if selected_folders != previous_folders:
            if not selected_folders:
                return
            # TODO impolement clean crawler call here
            # OLD : crawl_folders_iteratively(selected_folders)
