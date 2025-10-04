import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import (
    NamedTuple,
    runtime_checkable,
    Protocol,
    Iterable,
    Any,
    Iterator,
)


@runtime_checkable
class StatLike(Protocol):
    st_mtime: float
    st_ino: int
    st_dev: int


@runtime_checkable
class DirEntryLike(Protocol):
    path: str

    def is_dir(self) -> bool:
        ...

    def is_symlink(self) -> bool:
        ...

    def stat(self) -> StatLike:
        ...


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
    stat: FileStat | None

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


@runtime_checkable
class DirectoryScanner(Protocol):
    def __call__(self, directory: str | Path) -> Iterator[DirEntryLike]:
        ...


@runtime_checkable
class Filter(Protocol):
    def add(self, item: str) -> None:
        ...

    def __contains__(self, item: str) -> bool:
        ...


# Database Op Protocols


class ImageRow(NamedTuple):
    file_path: str
    randid: float
    mtime: float

    @classmethod
    def from_file_entry(cls, file_entry: FileEntry) -> "ImageRow":
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


class InsertRowsFunction(Protocol):
    def __call__(self, a: Iterable[ImageRow]) -> int:
        ...


class DatabaseBackend(ABC):
    """Abstract interface for database backends used in Draw-This."""

    @abstractmethod
    def initialize(self) -> None:
        """Establish a connection and prepare for access."""

    @abstractmethod
    def clear_all(self) -> None:
        """Remove all rows from the database (reset state)."""

    @abstractmethod
    def setup_schema(self) -> None:
        """Initialize database schema if not already created."""

    @abstractmethod
    def insert_rows(self, rows: Iterable[tuple]) -> int:
        """
        Insert multiple rows into the database.

        Args:
            rows: An iterable of row tuples matching schema.
        Returns:
            int: Number of rows successfully inserted.
        """

    @abstractmethod
    def remove_rows(self, paths: Iterable[str]) -> int:
        """
        Remove rows that match given file paths.

        Args:
            paths: Iterable of file paths to delete.
        Returns:
            int: Number of rows removed.
        """

    @abstractmethod
    def mark_seen(self, ids: Iterable[Any], seen: bool = True) -> int:
        """
        Update the 'seen' status of rows.

        Args:
            ids: Iterable of row IDs.
            seen: New seen status (default True).
        Returns:
            int: Number of rows updated.
        """

    @abstractmethod
    def shuffle(self) -> None:
        """
        Apply randomization strategy (if supported).
        For SQLite this might reorder rows, for other backends it may differ.
        """
