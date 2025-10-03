import os
import queue
import random
import sqlite3 as sql
import threading
from pathlib import Path
from typing import Iterable, Callable, Protocol, NamedTuple

from drawthis.utils.logger import logger

"""
SQLite file lister for Draw-This.

This module defines the file crawler and file loader that interact with a
permanent .db file in ~/.config/.
It has two main classes:

- Crawler:
Iteratively crawls through folders logic files in Breadth-first order allowing
for sorting.

- Loader:
Returns file paths listed in the SQL database as either a bulk list or in
batches of a given size.

Usage
-----
This file is imported as a package according to the following:
    import logic.file_listing
"""


class ImageRow(NamedTuple):
    file_path: str
    folder: str
    randid: float
    mtime: float


class MassCommitFN(Protocol):
    def __call__(self, a: Iterable[ImageRow]) -> int:
        pass


class DatabaseWriterError(Exception):
    pass


class CommitError(DatabaseWriterError):
    """Error when attempting to commit rows to chosen database."""


class DatabaseWriter:
    """
    Wraps storage and provides methods to access and commit, as to keep API
    consistent across storage methods and offer extensibility.

    Handles:
      - Schema setup / clearing
      - Batching paths before insert
      - Committing batches with file metadata (folder, mtime, random ID)

    This class defaults to SQLite3, but testability hooks
    (stat_fn, prepare_rows_fn, etc.) allow mocking the filesystem or row prep.
    Adding additional database types can be done by overriding the database
    connection (db_conn) and providing apropriate methods for manipulation.
    """

    COMMIT_BLOCK_SIZE = 1500
    # TODO Add schema versioning and migration
    DB_SCHEMA = (
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "path TEXT UNIQUE NOT NULL,"
        "folder TEXT,"
        "randid REAL,"
        "mtime REAL"
    )

    def __init__(
        self,
        db_path: str | Path = ":memory:",
        db_conn=None,
        commit_block_size=None,
        clear_database_fn=None,
        setup_schema_fn=None,
        insert_rows_fn: MassCommitFN = None,
    ):
        self.database = db_conn or sql.connect(
            db_path, check_same_thread=False
        )
        self.setup_schema = setup_schema_fn or self._setup_schema_sqlite3
        self.clear_database = clear_database_fn or self._clear_database_sqlite3
        self.insert_rows = insert_rows_fn or self._insert_rows_sqlite3
        self.commit_block_size = commit_block_size or self.COMMIT_BLOCK_SIZE

        self.loading_block: list[str] = []
        self.file_count = 0
        self._lock = threading.RLock()
        self._is_closed = False

        self.setup_schema()

    def __enter__(self) -> "DatabaseWriter":
        self._is_closed = False
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        with self._lock:
            try:
                self.flush()
            except CommitError:
                logger.error("Flush failed on exit.", exc_info=True)
            finally:
                self.database.close()
                self._is_closed = True

    def add_rows(self):
        pass

    def remove_rows(self):
        pass

    def update_seen(self):
        pass

    def flush(self, prepare_rows_fn: Callable = None) -> tuple[int, int]:
        """
        Inserts all paths in the loading_block into the database,
        generating a randid random float for each entry. Return a tuple
        showing rows attempted and rows inserted to check duplicates
        """
        with self._lock:
            batch = self.loading_block
            self.loading_block = []
            self.file_count = 0
        prepare_rows = prepare_rows_fn or gather_rows
        if not batch:
            return 0, 0
        attempted = len(batch)
        inserted = 0
        try:
            inserted = self.insert_rows(prepare_rows(batch))
        except Exception as e:
            # TODO: fail-fast mode only for development.
            # Switch to skip+log strategy in production.
            logger.exception(
                f"Commit error while writing {attempted} rows",
            )
            raise CommitError from e
        finally:
            logger.info(
                f"""
            Flush completed: attempted={attempted},
            inserted={inserted},
            skipped={attempted - inserted}""",
            )
        return attempted, inserted

    def add_path(self, path: str | Path) -> None:
        """
        Insert path in batch, write to DB if threshold reached.
        """
        if isinstance(path, Path):
            path = str(path)
        if not isinstance(path, str):
            raise ValueError("Entry not a valid path string")
        should_flush = False
        with self._lock:
            if self._is_closed:
                return
            self.loading_block.append(path)
            self.file_count += 1
            if self.file_count >= self.commit_block_size:
                should_flush = True
        if should_flush:
            self.flush()

    # Accessors

    @property
    def closed(self):
        return self._is_closed

    # SQLite 3 dependency private methods

    def _clear_database_sqlite3(self) -> None:
        """Clear the table in the database used to hold image paths."""
        cursor = self.database.cursor()
        cursor.execute("""DROP TABLE IF EXISTS image_paths""")
        cursor.close()

    def _setup_schema_sqlite3(self, db_schema: str = None):
        """Initialize the table in the database used to hold image paths."""
        db_schema = db_schema or self.DB_SCHEMA
        cursor = self.database.cursor()
        cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS image_paths ({db_schema})"""
        )
        cursor.close()

    def _insert_rows_sqlite3(self, rows: Iterable[tuple]) -> int:
        cursor = self.database.cursor()
        cursor.executemany(
            """
        INSERT OR IGNORE INTO
        image_paths(path, folder, randid, mtime)
         VALUES (?, ?, ?, ?)
        """,
            rows,
        )
        # NOTE: SELECT changes() is statement-local, safe after executemany
        cursor.execute("SELECT changes()")
        inserted = cursor.fetchone()[0]
        cursor.close()
        return inserted


# Helper functions


def gather_rows(file_batch, row_fn: Callable = None) -> Iterable[ImageRow]:
    row_fn = row_fn or build_row
    for file_path in file_batch:
        try:
            yield row_fn(file_path)
        except (FileNotFoundError, PermissionError, NotADirectoryError):
            logger.warning(
                f"File skipped: {file_path}",
            )
        except Exception:
            logger.error(
                "Unexpected error when gathering rows",
                exc_info=True,
            )
            raise


def build_row(file_path: str, stat_fn: Callable = None) -> ImageRow:
    stat_fn = stat_fn or os.stat
    return ImageRow(
        file_path=file_path,
        folder=os.path.dirname(file_path),
        randid=random.random(),
        mtime=stat_fn(file_path).st_mtime,
    )


class Crawler:
    """
    Walks directories recursively and yields file info objects.
    Guarantees:
    - Duplicate safe (Bloom filter)
    - Recursion safe (symlinks handled)
    - Skips inaccessible files gracefully

    Compromise:
    -May skip directories due to Bloom filter false positives (rare)
    """

    def __init__(
        self,
        on_start=None,
        on_end=None,
    ):
        self.on_start = on_start
        self.on_end = on_end

    # TODO Major refactor next:
    def crawl(
        self,
        root_dir: str | Path,
        dir_access_fn,
    ) -> Iterable[os.DirEntry]:
        """Yield every file in a folder iteratively."""
        dir_queue: queue.Queue = queue.Queue()
        dir_access_fn = dir_access_fn or os.scandir
        dir_queue.put(root_dir)
        self.on_start()
        while not dir_queue.empty():
            current_dir = dir_queue.get()
            try:
                for dir_entry in dir_access_fn(current_dir):
                    if dir_entry.is_dir():
                        dir_queue.put(dir_entry.path)
                        continue
                    yield dir_entry
            except (PermissionError, FileNotFoundError, NotADirectoryError):
                logger.warning(f"Skipped {current_dir}", exc_info=True)
        self.on_end()

    def clean_up(self):
        pass


class Loader:
    """Read all paths in a SQLite database, filtering and sorting them.

    Attributes:
        :ivar database: Connection to the SQLite database
    """

    def __init__(self, db_path=":memory:"):
        self.database = sql.connect(db_path)

    def total_db_loader(self) -> list:
        """Reads and returns ALL paths in the database in bulk."""
        cur = self.database.cursor()
        cur.execute(
            """
        SELECT  path, folder, randid, mtime
        FROM image_paths
        ORDER BY randid
        """
        )
        return [row[0] for row in cur.fetchall()]
