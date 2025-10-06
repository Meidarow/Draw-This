import random
from dataclasses import dataclass
from typing import (
    NamedTuple,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from drawthis.logic.core.protocols import DirEntryLike


class ImageRow(NamedTuple):
    file_path: str
    randid: float
    mtime: float

    @classmethod
    def from_file_entry(cls, file_entry: "FileEntry") -> "ImageRow":
        """
        Return an ImageRow object

        Args:
            file_entry FileEntry: Canonical file-system object for Draw-This

        Returns:
            ImageRow: Canonical database object for Draw-This
        """
        return ImageRow(
            file_path=file_entry.path,
            randid=random.random(),
            mtime=file_entry.stat.st_mtime,
        )


@dataclass
class FileStat:
    st_mtime: float
    st_ino: int
    st_dev: int


@dataclass(frozen=True)
class FileEntry:
    path: str
    is_dir: bool
    is_symlink: bool
    stat: "FileStat"

    @classmethod
    def from_dir_entry(cls, dir_entry: "DirEntryLike") -> "FileEntry":
        """
        Return a FileEntry object

        Args:
            dir_entry DirEntryLike: filesystem object

        Returns:
            FileEntry: Canonical file-system dataclass for Draw-This

        Notes:
            This method caches a DirEntryLike's attributes into a FileEntry
            directly to minimise syscalls in the database layer.
        """
        stat = dir_entry.stat()
        return cls(
            path=dir_entry.path,
            is_dir=dir_entry.is_dir(),
            is_symlink=dir_entry.is_symlink(),
            stat=FileStat(
                st_mtime=stat.st_mtime,
                st_ino=stat.st_ino,
                st_dev=stat.st_dev,
            ),
        )
