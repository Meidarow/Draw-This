from dataclasses import dataclass, field, replace
from enum import StrEnum
from typing import TYPE_CHECKING, Optional

from iteradraw.shared.types import PathLike

if TYPE_CHECKING:
    pass


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
