import sqlite3
from pathlib import Path
from typing import (
    Iterable,
    Callable,
    Optional,
    Any,
)

from drawthis.core.types import (
    DatabaseBackend,
)

# Type aliases:

PathLike = str | Path
FolderInput = PathLike | Iterable[PathLike]

"""
This module defines all backends with which the DatabaseManager from Draw-This
can interface. Each backend must be an override of the abstract class
'DatabaseBackend' and offer its minimal API.

This module includes one SQLite3Backend, the default databse solution for
Draw-This.

Contains:
SQLite3Backend

Notes:

"""


class DatabaseWriterError(Exception):
    pass


class CommitError(DatabaseWriterError):
    """Error when attempting to commit rows to chosen database."""


class SQLite3Backend(DatabaseBackend):
    """
    SQLite3 implementation of the Draw-This database backend.

    Handles schema setup, insertion, deletion, and flag updates
    for file metadata. Can be used as a context manager:

    Assumptions:
        Assumes all paths are normalised as absolute paths.

    Usage:
        with SQLite3Backend("~/.config/drawthis.db") as db:
            db.insert_rows([...])
    """

    DB_SCHEMA = """
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        path    TEXT UNIQUE NOT NULL,
        randid  REAL,
        mtime   REAL,
        seen    BOOLEAN DEFAULT 0
    """

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.database:
            try:
                self.database.close()
            finally:
                self.database = None

    def __init__(
        self,
        db_path: Optional[str] = None,
        connection: Optional[sqlite3.Connection] = None,
        on_insert: Callable = None,
        on_remove: Callable = None,
        on_mark_seen: Callable = None,
    ) -> None:
        self.db_path = db_path
        if db_path is None and connection is None:
            raise ValueError(
                "Must provide either db_path or an open sqlite3.Connection"
            )
        self.database = connection or sqlite3.connect(self.db_path)
        self.on_insert = on_insert
        self.on_remove = on_remove
        self.on_mark_seen = on_mark_seen

        self.setup_schema()
        self._configure_connection()

    def initialize(self) -> None:
        """Open the connection and ensure the schema exists."""
        self.setup_schema()  # create table if it isn’t there

    def clear_all(self) -> None:
        """Drop the table – caller should call `setup_schema` afterwards."""
        query = "DROP TABLE IF EXISTS image_paths"
        with self.database:
            self._execute(query)

    def setup_schema(self, db_schema: str | None = None) -> None:
        """Create `image_paths` with the supplied (or default) schema."""
        schema = db_schema or self.DB_SCHEMA
        query = f"CREATE TABLE IF NOT EXISTS image_paths ({schema})"
        with self.database:
            self._execute(query)

    def insert_rows(self, rows: Iterable[tuple[Any, ...]]) -> int:
        cursor = self.database.cursor()
        cursor.executemany(
            """
            INSERT OR IGNORE INTO image_paths (path, randid, mtime)
            VALUES (?, ?, ?)
            """,
            rows,
        )
        inserted = cursor.rowcount
        cursor.close()
        if self.on_insert:
            self.on_insert()
        return inserted

    def remove_rows(self, paths: Iterable[str]) -> int:
        with self.database:
            self.database.executemany(
                """
                DELETE FROM image_paths
                WHERE path = ?
                """,
                [(p,) for p in paths],
            )
            cur = self.database.execute("SELECT changes()")
            removed = cur.fetchone()
        if self.on_remove:
            self.on_remove()
        return removed[0] or 0

    def mark_seen(self, paths: Iterable[str], seen: bool = True) -> int:
        """
        Set the `seen` flag for the supplied paths.
        `paths` is an iterable of path strings.
        """
        with self.database:
            self.database.executemany(
                """
                UPDATE image_paths
                SET seen = ?
                WHERE path = ?
                """,
                [(int(seen), p) for p in paths],
            )
            cur = self.database.execute("SELECT changes()")
            marked = cur.fetchone()
        if self.on_mark_seen:
            self.on_mark_seen()
        return marked[0] or 0

    def shuffle(self) -> None:
        """
        Assign a new random float in [0, 1) to the `randid` column of each row.
        """
        query = """
            UPDATE image_paths
            SET randid = ABS(RANDOM()) / 9223372036854775808.0
        """
        with self.database:
            self._execute(query)

    # Non-default backend methods

    def load_whole_database(self) -> list:
        """Return all entries from the database."""
        query = """
        SELECT  path, randid, mtime
        FROM image_paths
        ORDER BY randid
        """
        cur = self.database.execute(query)
        rows = cur.fetchall()
        return [row[0] for row in rows]

    def count_rows(self) -> int:
        cur = self._execute("SELECT COUNT(*) FROM image_paths")
        return cur.fetchone()[0] or 0

    def commit(self) -> None:
        """Explicitly commit any pending transaction."""
        try:
            if self.database:
                self.database.commit()
                self.database.execute("PRAGMA wal_checkpoint(FULL);")
        except sqlite3.DatabaseError as e:
            raise CommitError("Failed to commit to database") from e

    def _configure_connection(self):
        self.database.execute("PRAGMA journal_mode = WAL;")
        self.database.execute("PRAGMA synchronous = NORMAL;")
        self.database.execute("PRAGMA temp_store = MEMORY;")
        self.database.execute("PRAGMA foreign_keys = ON;")

    def _execute(self, query: str, *params: Any) -> sqlite3.Cursor:
        """Run a single statement with optional parameters."""
        return self.database.execute(query, params)
