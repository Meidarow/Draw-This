from pathlib import Path

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    pass


# =============================================================================
# Settings - Extra slideshow/Idle domain
# =============================================================================

"""
This module holds the definitions for all dataclasses used by the
AppSettingsService.

Dataclasses:
-AppSettings: Set of all parameters outside a Draw-This session.
-FolderSet: Wrapper for folders with enabled/disabled flag.
-TimerSet: Wrapper for timers.

Enums:
-APPSETTINGS.FIELDS: Reflects fields of AppSettings, centralizing refactors
-APPSETTINGS.DEFAULTS: Defines sane defaults for all fields of AppSettings
"""


@dataclass
class FolderSet:
    """
    Wrapper for a set of folders

    Guarantees:
    - Folders are always unique (no duplicates), keyed by folder name
    """

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

    @property
    def enabled(self) -> list[str]:
        """Return only enabled folders."""
        return [f for f, e in self._folders.items() if e]

    @property
    def disabled(self) -> list[str]:
        """Return only disabled folders."""
        return [f for f, e in self._folders.items() if not e]

    @property
    def all(self) -> dict[str, bool]:
        """Raw view of all folders and states."""
        return dict(self._folders)

    def copy(self) -> "FolderSet":
        """Return identical copy of self"""
        return FolderSet(_folders=self.all)


@dataclass
class TimerSet:
    """
    Wrapper for a set of timers

    Guarantees:
    - List is always sorted
    - No duplicate timers can be inserted
    """

    _timers: list[int] = field(default_factory=list)

    @classmethod
    def from_list(cls, timers: list[int]) -> "TimerSet":
        """Factory for TimerSet from list of timers"""
        ts = cls()
        for timer in timers:
            ts.add(timer)
        return ts

    def add(self, timer: int) -> None:
        """Add a new timer if not already present, then sort timer list"""
        if timer in self._timers:
            return
        self._timers.append(timer)
        self._timers = sorted(self._timers)

    def remove(self, timer: int) -> None:
        """Remove a timer"""
        self._timers.remove(timer)

    @property
    def all(self) -> list[int]:
        """Raw view of all timers"""
        return list(self._timers)

    def copy(self) -> "TimerSet":
        """Return identical copy of self"""
        return TimerSet(_timers=self.all)


class APPSETTINGS:
    class FIELDS(StrEnum):
        """
        Define field keys and sane defaults for Session.

        New fields may be added by:
          - Adding it here AND in Session as follows:
          ENUM_FIELD_NAME = "session_attribute_name"
        """

        TIMERS = "timers"
        FOLDERS = "folders"

    class DEFAULTS:
        SETTINGS_DIR = Path().home() / ".config" / "drawthis"
        FILE_NAME = "config.json"


@dataclass
class AppSettings:
    timers: TimerSet = field(default_factory=TimerSet)
    folders: FolderSet = field(default_factory=FolderSet)

    @classmethod
    def from_dict(cls, session_dict: dict) -> "AppSettings":
        return cls(
            timers=TimerSet.from_list(
                session_dict.get(APPSETTINGS.FIELDS.TIMERS, [])
            ),
            folders=FolderSet.from_pairs(
                list(session_dict.get(APPSETTINGS.FIELDS.FOLDERS, {}).items())
            ),
        )

    def to_dict(self) -> dict:
        session_dict = {
            APPSETTINGS.FIELDS.TIMERS: self.timers.all,
            APPSETTINGS.FIELDS.FOLDERS: self.folders.all,
        }
        return session_dict

    def copy(self) -> "AppSettings":
        return AppSettings(
            timers=self.timers.copy(),
            folders=self.folders.copy(),
        )
