from dataclasses import dataclass, field, replace
from enum import StrEnum
from typing import TYPE_CHECKING, Optional

from drawthis.core.protocols.protocols import Model
from drawthis.core.types import PathLike

if TYPE_CHECKING:
    pass


# =============================================================================
# Settings - Extra slideshow/Idle domain
# =============================================================================

"""
This module holds the definitions for all dataclasses used by the
AppSettingsService.

Dataclasses:
-AppSettings: Set of all parameters outside a Draw-This resources.
-FolderSet: Wrapper for folders with enabled/disabled flag.
-TimerSet: Wrapper for timers.

Enums:
-APPSETTINGS.FIELDS: Reflects fields of AppSettings, centralizing refactors
-APPSETTINGS.DEFAULTS: Defines sane defaults for all fields of AppSettings
"""


@dataclass(frozen=True)
class Folder:
    path: PathLike
    enabled: bool
    display_name: Optional[str] = None

    class Fields(StrEnum):
        PATH = "path"
        NAME = "name"
        ENABLED = "enabled"

    @classmethod
    def from_dict(cls, data):
        return Folder(
            path=data[cls.Fields.PATH],
            enabled=data[cls.Fields.ENABLED],
            display_name=data[cls.Fields.NAME],
        )

    def to_dict(self) -> dict[str, PathLike | str | bool]:
        """Return serialized dict of Folder object."""
        return {
            self.Fields.PATH: self.path,
            self.Fields.NAME: self.display_name,
            self.Fields.ENABLED: self.enabled,
        }


@dataclass(frozen=True)
class FolderSet(Model):
    """
    Wrapper for a set of folders

    Guarantees:
    - Folders are always unique (no duplicates), keyed by folder path
    """

    _folders: list[Folder] = field(default_factory=list)

    class State(StrEnum):
        ENABLED = "enabled"
        PARTIAL = "partial"
        DISABLED = "disabled"

    @classmethod
    def from_dict(cls, data):
        folders = data["folders"]
        if not folders:
            raise ValueError("No valid folders given")
        return cls(_folders=[Folder.from_dict(fd) for fd in folders])

    def add(self, path: str, enabled: bool = True) -> "FolderSet":
        """Add a folder with optional enabled state."""
        if any(folder.path == path for folder in self._folders):
            return self
        new_data = self._folders + [Folder(path=path, enabled=enabled)]
        return replace(self, _folders=new_data)

    def remove(self, path: str) -> "FolderSet":
        """Remove a folder."""
        new_data = [folder for folder in self._folders if folder.path != path]
        return replace(self, _folders=new_data)

    def set_folder_enabled(self, path: str, enabled: bool) -> "FolderSet":
        """Enable a folder explicitly."""
        new_data = [
            replace(folder, enabled=enabled) if folder.path == path else folder
            for folder in self._folders
        ]
        return replace(self, _folders=new_data)

    def to_dict(self) -> list[dict[str, bool]]:
        """Raw view of all folders and states."""
        return [item.to_dict() for item in self._folders]

    # Accessors

    @property
    def enabled(self) -> list[str]:
        """Return only enabled folders."""
        return [folder.path for folder in self._folders if folder.enabled]

    @property
    def disabled(self) -> list[str]:
        """Return only disabled folders."""
        return [folder.path for folder in self._folders if not folder.enabled]

    @property
    def state(self) -> "FolderSet.State":
        """Return enabled status for FolderSet"""
        if not self._folders:
            return FolderSet.State.DISABLED

        enabled_count = sum(1 for item in self._folders if item.enabled)

        if enabled_count == len(self._folders):
            return FolderSet.State.ENABLED
        elif enabled_count == 0:
            return FolderSet.State.DISABLED
        else:
            return FolderSet.State.PARTIAL


@dataclass(frozen=True)
class TimerSet(Model):
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

    def add(self, timer: int) -> "TimerSet":
        """Add a new timer if not already present, then sort timer list"""
        if timer in self._timers:
            return self
        timers = self._timers.copy()
        timers.append(timer)
        timers = sorted(timers)
        return replace(self, _timers=timers)

    def remove(self, timer: int) -> "TimerSet":
        """Remove a timer"""
        timers = self._timers.copy()
        timers.remove(timer)
        return replace(self, _timers=timers)

    @property
    def all(self) -> list[int]:
        """Raw view of all timers"""
        return list(self._timers)
