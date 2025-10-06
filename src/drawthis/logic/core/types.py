from abc import ABC, abstractmethod
from typing import (
    Iterable,
    Any,
)


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
