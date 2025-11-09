from dataclasses import dataclass, field, replace
from enum import StrEnum
from typing import TYPE_CHECKING

from iteradraw.shared.types import PathLike

if TYPE_CHECKING:
    pass

"""
Canonical dataclass and value object for handling folders in Iteradraw.
A Folder is a pure value-object that only exists in the context of a
FolderSet, its root aggregate.

Classes:
    Folder: value object holding path to directory and selection status.
    FolderSet: aggregate of folders and behavior definitions for domain.

Usage:

"""


@dataclass(frozen=True)
class Folder:
    path: PathLike
    enabled: bool


@dataclass(frozen=True)
class FolderSet:
    """
    Wrapper for a set of folders

    Guarantees:
    - Folders are always unique (no duplicates), keyed by folder path
    """

    name: str
    _folders: dict[str, Folder] = field(default_factory=list)

    class State(StrEnum):
        ENABLED = "enabled"
        PARTIAL = "partial"
        DISABLED = "disabled"

    def add(self, path: str, enabled: bool = True) -> "FolderSet":
        """Add a folder with optional enabled state."""
        if self._folders[path]:
            return self
        new_data = self._folders.copy()
        new_data[path] = Folder(path=path, enabled=enabled)
        return replace(self, _folders=new_data)

    def remove(self, path: str) -> "FolderSet":
        """Remove a folder."""
        new_data = self._folders.copy()
        new_data.pop(path)
        return replace(self, _folders=new_data)

    def set_folder_enabled(self, path: str, enabled: bool) -> "FolderSet":
        """Enable a folder explicitly."""
        new_data = self._folders.copy()
        new_data[path] = replace(new_data[path], enabled=enabled)
        return replace(self, _folders=new_data)

    # Accessors

    @property
    def all(self) -> list[Folder]:
        """Return all folders."""
        return list(self._folders.values())

    @property
    def enabled(self) -> list[Folder]:
        """Return only enabled folders."""
        return [folder for folder in self._folders.values() if folder.enabled]

    @property
    def disabled(self) -> list[Folder]:
        """Return only disabled folders."""
        return [
            folder for folder in self._folders.values() if not folder.enabled
        ]

    @property
    def state(self) -> "FolderSet.State":
        """Return enabled status for FolderSet"""
        if not self._folders:
            return FolderSet.State.DISABLED

        enabled_count = sum(
            1 for item in self._folders.values() if item.enabled
        )

        if enabled_count == len(self._folders):
            return FolderSet.State.ENABLED
        elif enabled_count == 0:
            return FolderSet.State.DISABLED
        else:
            return FolderSet.State.PARTIAL
