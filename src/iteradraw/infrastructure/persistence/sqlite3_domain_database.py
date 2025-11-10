import sqlite3
from typing import (
    Optional,
    Any,
)

from iteradraw.domain.exceptions import (
    CommitError,
    PersistenceError,
    ObjectNotFoundError,
)
from iteradraw.domain.models.folder import FolderSet, Folder

"""
This module defines all backends with which the DatabaseManager from Draw-This
can interface. Each backend must be an override of the abstract class
'DatabaseBackend' and offer its minimal API.

This module includes one SQLite3ImagePathBackend, the default databse solution 
for Iteradraw.

Contains:
SQLite3ImagePathBackend

Notes:

"""


class SQLite3DomainDatabase:
    """
    SQLite3 implementation of the Iteradraw domain database backend.

    Handles schema setup, insertion, deletion, and flag updates
    for file metadata. Can be used as a context manager:

    Assumptions:
        Assumes all paths are normalised as absolute paths.

    Usage:
        with SQLite3Backend("~/.config/drawthis.db") as db:
            db.insert_rows([...])
    """

    DB_SCHEMA = """
    CREATE TABLE IF NOT EXISTS foldersets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    );
    CREATE TABLE IF NOT EXISTS folders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT UNIQUE NOT NULL,
        enabled BOOLEAN DEFAULT 1,
        folderset_id INTEGER NOT NULL,
        FOREIGN KEY(folderset_id) REFERENCES foldersets(id)
            ON DELETE CASCADE
    );
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
    ) -> None:
        self.db_path = db_path
        if db_path is None and connection is None:
            raise ValueError(
                "Must provide either db_path or an open sqlite3.Connection"
            )
        self.database = connection or sqlite3.connect(self.db_path)
        self.database.row_factory = sqlite3.Row
        self.setup_schema()
        self._configure_connection()

    def initialize(self) -> None:
        """Open the connection and ensure the schema exists."""
        self.setup_schema()  # create table if it isn’t there

    def clear_all(self) -> None:
        """Drop all domain tables."""
        query = """
        DROP TABLE IF EXISTS folders;
        DROP TABLE IF EXISTS foldersets;
        """
        with self.database:
            self.database.executescript(query)

    def setup_schema(self, db_schema: str | None = None) -> None:
        """Create table with the supplied (or default) schema."""
        query = db_schema or self.DB_SCHEMA
        with self.database:
            self.database.executescript(query)

    def get_folderset(self, name: str) -> FolderSet:
        """
        Retrieves one FolderSet from the DB and reconstructs the aggregate.
        """
        rows = self._execute(
            """
            SELECT f.path, f.enabled
            FROM folders f
            JOIN foldersets fs ON f.folderset_id = fs.id
            WHERE fs.name = ?
            """,
            (name,),
        ).fetchall()

        if not rows:
            raise ObjectNotFoundError(f"No FolderSet found with name: {name}")

        return FolderSet(
            name=name,
            _folders={
                row["path"]: Folder(row["path"], row["enabled"])
                for row in rows
            },
        )

    def get_all_foldersets(self) -> list[FolderSet]:
        """
        Retrieves all FolderSets from the DB and reconstructs them.
        """

        # 1. Get ALL data in one go
        query = """
        SELECT
            fs.name,
            f.path,
            f.enabled
        FROM
            foldersets fs
        JOIN
            folders f ON f.folderset_id = fs.id
        ORDER BY
            fs.name;
        """

        # This holds the in-progress foldersets: { "name": { "path": folder } }
        foldersets_map = {}

        # 2. Loop through the flat results
        # (Assuming your _execute.fetchall() returns dict-like rows)
        for row in self._execute(query).fetchall():
            name = row["name"]

            # 3. Create the FolderSet if it's the first time we've seen it
            if name not in foldersets_map:
                foldersets_map[name] = {}

            # 4. Add the folder to its set
            foldersets_map[name][row["path"]] = Folder(
                path=row["path"], enabled=row["enabled"]
            )

        # 5. Convert the map into the final list of objects
        return [
            FolderSet(name=name, _folders=folders)
            for name, folders in foldersets_map.items()
        ]

    def save_folderset(self, folderset: FolderSet):
        """
        Saves a FolderSet aggregate to the DB in a transaction.
        """
        try:
            with self.database:  # This automatically BEGINs a transaction
                # Upsert the parent folderset
                cursor = self._execute(
                    """
                    INSERT INTO foldersets (name) VALUES (?)
                    ON CONFLICT(name) DO UPDATE SET name=excluded.name
                    RETURNING id
                    """,
                    (folderset.name,),
                )
                folderset_id = cursor.fetchone()["id"]

                # Nuke old folders for this set (simple, effective)
                self._execute(
                    "DELETE FROM folders WHERE folderset_id = ?",
                    (folderset_id,),
                )

                # Insert new folders
                folder_data = [
                    (f.path, f.enabled, folderset_id) for f in folderset.all
                ]
                if folder_data:  # executemany fails on empty list
                    self.database.executemany(
                        """
                        INSERT INTO folders (path, enabled, folderset_id)
                        VALUES (?, ?, ?)
                        """,
                        folder_data,
                    )
        except sqlite3.DatabaseError as e:
            raise PersistenceError("Failed to save folderset") from e

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
