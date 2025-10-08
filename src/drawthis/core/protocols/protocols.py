import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import (
    Iterable,
    Any,
    Optional,
    Callable,
)
from typing import (
    runtime_checkable,
    Protocol,
    Iterator,
)

from drawthis.core.types import PathLike


# =============================================================================
# Filesystem and Database Persistence - Session domain
# =============================================================================

# Filesystem


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

    def stat(self) -> "StatLike":
        ...


@runtime_checkable
class FilterLike(Protocol):
    def add(self, item: str) -> None:
        ...

    def __contains__(self, item: str) -> bool:
        ...


@runtime_checkable
class DirectoryScanner(Protocol):
    def __call__(self, directory: str | Path) -> Iterator["DirEntryLike"]:
        ...


# Database


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


# =============================================================================
# JSON Persistence - Settings domain only (for slideshow and app)
# =============================================================================
#   This module could be slightly modified to use generic typevars,
#   together with a universal Model base-class as template for all
#   "settings domain" Model dataclasses.


class Persistence(Protocol):
    def read_file(self):
        ...

    def write_file(self, model_object):
        ...


class JsonSettingsPersistence(Persistence, ABC):
    def __init__(
        self,
        settings_dir_path: PathLike,
        file_name: str,
        model_cls: Any,
        on_write_error: Optional[Callable],
        on_read_error: Optional[Callable],
    ):
        self.settings_dir_path = Path(settings_dir_path)
        self.settings_dir_path.mkdir(parents=True, exist_ok=True)
        self.settings_file = self.settings_dir_path / file_name
        self.model_cls = model_cls
        self.on_read_error = on_read_error
        self.on_write_error = on_write_error

    def read_file(self):
        """Parse file and restores previous session's final values."""
        if not self.settings_file.exists():
            self.settings_file.touch()
        data = None
        try:
            with open(self.settings_file, "r", encoding="utf-8") as config:
                data = json.load(config)
        except (json.JSONDecodeError, FileNotFoundError):
            if self.on_read_error:
                self.on_read_error()
        defaults = self._make_default_dict()
        merged = defaults.copy()
        if data:
            merged.update({k: v for k, v in data.items() if k in defaults})
        return self._make_object(merged)

    def write_file(self, model_object):
        """Create file and stores the current session's values."""
        model_object_dict = self._make_dict(model_object)
        try:
            self._safe_json_write(self.settings_file, model_object_dict)
        except FileNotFoundError:
            if self.on_write_error:
                self.on_write_error()

    @staticmethod
    def _safe_json_write(path: Path, data: dict) -> None:
        tmp = path.with_suffix(path.suffix + ".tmp")

        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        tmp.replace(path)

    @staticmethod
    def _make_dict(model_object) -> dict:
        return model_object.to_dict()

    def _make_object(self, model_object_dict):
        return self.model_cls.from_dict(model_object_dict)

    def _make_default_dict(self) -> dict:
        return self.model_cls().to_dict()
