from abc import ABC, abstractmethod
from typing import (
    Iterable,
    Any,
)
from typing import (
    Protocol,
)

"""
Interface protocols for the persistence layer of Iteradraw.

This module defines protocols that apply generically and universally to all 
backend implementations meant for persistence, with the intention of 
simplyfying persistence operations, encapsulating persistence domain 
knowledge to its layer and allowing hot-swapping of backends

Iteradraw uses persistence in two ways: settings and session storage for 
user-preferences and content, and for resource management during slideshow 
sessions. 

Classes:
    DatabaseBackend: protocol for session resource management backends.
    Persistence: protocol for settings/user-prefs/content backends.
 
Usage:

"""


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


class Persistence(Protocol):
    """
    Persistence protocol for domain objects, intended for user-preferences
    and content.

    Defines API that must be public in concrete implementations for
    hot-swappale backends to properly be consumed by the repository layer.
    """

    def read_file(self): ...

    def write_file(self, namespace): ...
