import os
import queue
import random
import sqlite3 as sql
import threading
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, Callable, Protocol, NamedTuple, Any

from pybloom_live import BloomFilter

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


class SQLite3Backend(DatabaseBackend):
    # TODO Add schema versioning and migration
    DB_SCHEMA = """
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT UNIQUE NOT NULL,
        folder TEXT,
        randid REAL,
        mtime REAL
        """
    migration = {}

    def __init__(self, db_path: str = None):
        self.db_path = db_path
        self.database = sql.Connection = None

    def initialize(self) -> None:
        self.database = sql.connect(self.db_path)

    def clear_all(self) -> None:
        """Clear the table in the database used to hold image paths."""
        cursor = self.database.cursor()
        cursor.execute("""DROP TABLE IF EXISTS image_paths""")
        cursor.close()

    def setup_schema(self, db_schema: str = None):
        """Initialize the table in the database used to hold image paths."""
        db_schema = db_schema or self.DB_SCHEMA
        cursor = self.database.cursor()
        cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS image_paths ({db_schema})"""
        )
        cursor.close()

    def insert_rows(self, rows: Iterable[tuple]) -> int:
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

    def remove_rows(self, paths: Iterable[str]) -> int:
        pass

    def mark_seen(self, ids: Iterable[Any], seen: bool = True) -> int:
        pass

    def shuffle(self) -> None:
        pass


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
    # TODO onsider splitting into orchestration layer that can handle policy
    """

    COMMIT_BLOCK_SIZE = 1500

    def __init__(
        self,
        db_path: str | Path = ":memory:",
        db_conn=None,
        commit_block_size=None,
        backend=None,
    ):
        self.database = db_conn or sql.connect(
            db_path, check_same_thread=False
        )
        self.backend = backend or SQLite3Backend()
        self.commit_block_size = commit_block_size or self.COMMIT_BLOCK_SIZE

        self.loading_block: list[str] = []
        self.file_count = 0
        self._lock = threading.RLock()
        self._is_closed = False

    def __enter__(self) -> "DatabaseWriter":
        self._is_closed = False
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        with self._lock:
            try:
                self._flush()
            except CommitError:
                logger.error("Flush failed on exit.", exc_info=True)
            finally:
                self.database.close()
                self._is_closed = True

    def add_rows(self, file_generator: Iterable) -> None:
        """
        Add rows into the database additively.

        This method accepts files from a generator and adds them to the
        existing database. It serves to avoid re-crawling folders that had
        already been selected previously.

        Args:
            file_generator (Generator): Iterable of files to be added

        Returns:


        Raises:


        Examples:

        """
        pass

    def remove_rows(self):
        """
        Remove rows of paths under given directory from database

        This method removes all rows with paths under the provided parent
        directories.

        Args:
            parent_folders list[str]: Parent directories to be removed

        Returns:


        Raises:


        Examples:

        """

    def update_seen(self):
        pass

    def _flush(self, prepare_rows_fn: Callable = None) -> tuple[int, int]:
        """
        Dump all file paths currently in batch and clear batch

        Inserts all paths in the loading_block into the database,
        generating a randid random float for each entry. Return a tuple
        showing rows attempted and rows inserted to check duplicates

        Args:
            prepare_rows_fn (Callable, optional): Function that transforms
            batch into rows ready for insertion. Defaults to `gather_rows`.

        Returns:
            tuple[int,int]: (attempted, inserted), showing number of rows
                attempted and number of rows actually inserted.

        Raises:
            CommitError: If insertion fails. The original exception is chained.

        Examples:
            > flush(batch_preparer)
            (42, 40)
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


def build_row(file_entry: os.DirEntry, with_stat: bool = False) -> ImageRow:
    """
    Assemble an ImageRow object

    This method uses a DirEntry directly to avoid syscalls and assembles rows
    ready for database insertion. Performing os.stat() is optional.

    Args:
        file_entry os.DirEntry: filesystem object assemble row from
        with_stat bool: Enable os.stat() call, currently for st_mtime

    Returns:
        ImageRow: Assempled ImageRow object ready for storage

    Raises:
        FileNotFoundError: log and skip

    Examples:
        >row = build_row(parent/directory/file, True)
        >print(row.file_path)
        'parent/directory/file'
        >print(row.mtime)
        '123456789.0'
        >print(row.folder)
        'parent/directory'
    """
    st_mtime = file_entry.stat().st_mtime if with_stat else None
    row = None
    try:
        row = ImageRow(
            file_path=file_entry.path,
            folder=os.path.dirname(file_entry.path),
            randid=random.random(),
            mtime=st_mtime,
        )
    except FileNotFoundError:
        logger.warning(
            f"File not found when assembling row: {file_entry.path}"
        )
    return row


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
        dir_access_fn=None,
        bloom_filter_cap=100000,
        bloom_filter_error_rate=0.001,
    ):
        self.on_start = on_start
        self.on_end = on_end
        self.dir_access = dir_access_fn or os.scandir
        self.dir_queue: queue.Queue = queue.Queue()
        self.filter = BloomFilter(
            capacity=bloom_filter_cap, error_rate=bloom_filter_error_rate
        )

    def crawl(self, folders: list[str | Path]) -> Iterable[os.DirEntry]:
        """Yield every file in a folder iteratively."""
        self.enqueue_list(folders)

        if self.on_start:
            self.on_start()

        while not self.dir_queue.empty():
            current_dir = self.dir_queue.get()
            try:
                yield from self.check_dir_and_yield(current_dir)
            except (
                PermissionError,
                FileNotFoundError,
                NotADirectoryError,
            ):
                logger.warning(f"Skipped {current_dir}", exc_info=True)

        if self.on_end:
            self.on_end()

    def check_dir_and_yield(self, directory):
        for entry in self.dir_access(directory):
            # Resolve symlinks safely
            try:
                is_symlink = entry.is_symlink()
            except OSError:  # e.g. broken link
                is_symlink = False

            if is_symlink:
                # decide policy – here we skip them
                continue

            if entry.is_dir(follow_symlinks=False):
                # store absolute path for bloom filter
                abs_path = os.path.abspath(entry.path)
                self.dir_queue.put(abs_path)
                continue

            yield entry

    def enqueue_list(self, folder_list: list[str]):
        for directory in folder_list:
            abs_path = os.path.abspath(str(directory))
            if abs_path not in self.filter:
                self.filter.add(abs_path)
                self.dir_queue.put(abs_path)

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
