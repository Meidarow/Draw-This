import os
import queue
import random
import sqlite3 as sql
import threading
from pathlib import Path
from typing import (
    Iterable,
    Callable,
    Any,
    Generator,
    Optional,
)

from pybloom_live import BloomFilter

from drawthis.logic.protocols import (
    DatabaseBackend,
    ImageRow,
    DirectoryScanner,
    Filter,
    FileEntry,
)
from drawthis.utils.logger import logger

# Type aliases:

PathLike = str | Path
FolderInput = PathLike | Iterable[PathLike]


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


class DatabaseWriterError(Exception):
    pass


class CommitError(DatabaseWriterError):
    """Error when attempting to commit rows to chosen database."""


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
        self.database: sql.Connection | None = None

    def initialize(self) -> None:
        self.database = sql.connect(self.db_path)

    def clear_all(self) -> None:
        """Clear the table in the database used to hold image paths."""
        cursor = self.database.cursor()
        cursor.execute("""DROP TABLE IF EXISTS image_paths""")
        cursor.close()

    def setup_schema(self, db_schema: str = None) -> None:
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
        cursor = self.database.cursor()
        cursor.execute()
        cursor.close()
        return 0

    def mark_seen(self, ids: Iterable[Any], seen: bool = True) -> None:
        cursor = self.database.cursor()
        cursor.execute()
        cursor.close()

    def shuffle(self) -> None:
        cursor = self.database.cursor()
        cursor.execute()
        cursor.close()


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

    def add_path(self, path: PathLike) -> None:
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
    row_fn = row_fn or build_row_from
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


def build_row_from(file_entry: FileEntry) -> ImageRow:
    """
    Return an ImageRow object

    Args:
        file_entry FileEntry: Canonical file-system object for Draw-This

    Returns:
        ImageRow: Canonical database object for Draw-This
    """
    return ImageRow(
        file_path=file_entry.path,
        folder=file_entry.stat.parent_dir,
        randid=random.random(),
        mtime=file_entry.stat.st_mtime,
    )


class Crawler:
    """
    Walks directories recursively and yields DirEntry objects.
    Guarantees:
    - Duplicate safe (Bloom filter)
    - Recursion safe (symlinks handled)
    - Skips inaccessible files gracefully

    Compromise:
    -May skip directories due to Bloom filter false positives (rare)

    Notes:
        -Converts DirEntryLike objects into static FileEntry objects
        -Use as a context manager for automatic cleanup, or manage cleanup
         manually via clear_queue() / reset_state() for long-lived crawlers.
    """

    def __init__(
        self,
        on_start: Callable | None = None,
        on_end: Callable | None = None,
        on_skip: Callable[[str, Exception], None] | None = None,
        dir_access_fn: DirectoryScanner = None,
        bloom_filter: Optional[Filter] = None,
    ):
        self.on_start = on_start
        self.on_end = on_end
        self.on_skip = on_skip
        self.directory_queue: queue.Queue[str] = queue.Queue()
        self.dir_access = dir_access_fn or os.scandir
        self.filter = bloom_filter
        self._files_skipped = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clear_queue()
        self._files_skipped = 0
        self.filter = None

    def clear_queue(self):
        """Clear directory queue"""
        while not self.directory_queue.empty():
            self.directory_queue.get()

    def reset_state(
        self,
        bloom_filter: Optional[Filter] = None,
        bloom_filter_cap: int = 100000,
        bloom_filter_error_rate: float = 0.001,
    ):
        """Reset Crawler for re-use, also resets skipped files counter"""
        self._files_skipped = 0
        self.clear_queue()
        self.filter = bloom_filter or BloomFilter(
            capacity=bloom_filter_cap, error_rate=bloom_filter_error_rate
        )

    def crawl(self, folders: FolderInput) -> Generator[FileEntry]:
        """Yield os.DirEntry objects for every file found in folders."""
        self._enqueue(folders)

        if self.on_start:
            self.on_start()

        while not self.directory_queue.empty():
            current_directory = self.directory_queue.get()
            try:
                yield from self._generate_entries_from(current_directory)
            except (
                PermissionError,
                FileNotFoundError,
                NotADirectoryError,
            ) as e:
                self._files_skipped += 1
                if self.on_skip:
                    self.on_skip(current_directory, e)
                else:
                    logger.warning(
                        f"Skipped {current_directory}", exc_info=True
                    )

        if self.on_end:
            self.on_end()

    # Accessors for internal metrics

    @property
    def files_skipped(self):
        return self._files_skipped

    # Private Helpers

    def _generate_entries_from(
        self, directory: PathLike
    ) -> Generator[FileEntry, None, None]:
        for entry in self.dir_access(str(directory)):
            file_entry = FileEntry.from_dir_entry(entry)

            if file_entry.is_symlink:
                # decide policy – here we skip them
                continue

            if file_entry.is_dir:
                # store absolute path for bloom filter
                self._enqueue(file_entry.path)
                continue

            yield file_entry

    def _enqueue(self, folders: FolderInput):
        """Add folders to Crawler's queue"""
        for directory in self._as_iterable(folders):
            try:
                absolute_path = self._normalise_path(directory)
                if absolute_path not in self.filter:
                    self.filter.add(absolute_path)
                    self.directory_queue.put(absolute_path)
            except OSError:  # e.g. broken link
                logger.warning("Relative to absolute path conversion failed")

    @staticmethod
    def _normalise_path(p: PathLike) -> str:
        """Return absolute path from relative path"""
        return os.path.abspath(str(p))

    @staticmethod
    def _as_iterable(item: FolderInput) -> Iterable[PathLike]:
        """Convert to iterable"""
        if isinstance(item, (str, Path)):
            return [item]
        if isinstance(item, Iterable):
            return item
        raise TypeError(f"Invalid type: {type(item)}")


# class Loader:
#     """Read all paths in a SQLite database, filtering and sorting them.
#
#     Attributes:
#         :ivar database: Connection to the SQLite database
#     """
#
#     def __init__(self, db_path=":memory:"):
#         self.database = sql.connect(db_path)
#
#     def total_db_loader(self) -> list:
#         """Reads and returns ALL paths in the database in bulk."""
#         cur = self.database.cursor()
#         cur.execute(
#             """
#         SELECT  path, folder, randid, mtime
#         FROM image_paths
#         ORDER BY randid
#         """
#         )
#         return [row[0] for row in cur.fetchall()]
