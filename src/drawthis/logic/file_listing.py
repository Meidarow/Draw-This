import os
import queue
import sqlite3
import threading
from pathlib import Path
from typing import (
    Iterable,
    Callable,
    Generator,
    Optional,
    Any,
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
        with self.database:
            self.database.executemany(
                """
                INSERT OR IGNORE INTO image_paths
                    (path, randid, mtime)
                VALUES (?, ?, ?)
                """,
                rows,
            )
            cur = self.database.execute("SELECT changes()")
            inserted = cur.fetchone()
        if self.on_insert:
            self.on_insert()
        return inserted[0] or 0

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

    def count_rows(self) -> int:
        cur = self._execute("SELECT COUNT(*) FROM image_paths")
        return cur.fetchone()[0] or 0

    def commit(self) -> None:
        """Explicitly commit any pending transaction."""
        try:
            if self.database:
                self.database.commit()
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


class DatabaseWriter:
    """
    Orchestrates database operations and provides API to add and remove rows,
    mark files as seen for session persistence and randomize the database.

    Handles:
      - Batching paths before insert
      - Committing batches with file metadata (folder, mtime, random ID)
      TODO Add filtering by file type

    Notes:
        -This class is meant to handle ImageRow objects, the canonical
         dataclass for the database layer of Draw-This.
        -This class defaults to the SQLite 3 backend implementation, however it
         is database agnostic. You may extend it by implementing a new
         database according to the abstract class DatabaseBackend.
    """

    def __init__(
        self,
        db_path: PathLike = ":memory:",
        batch_size=None,
        backend=None,
        crawler=None,
    ):
        self.backend = backend or SQLite3Backend(db_path)
        self.crawler_class = crawler or Crawler
        self.batch_size = batch_size or 1500

        self.loading_block: list[str] = []
        self.file_count = 0
        self._lock = threading.RLock()
        self._is_closed = False

    def add_rows(self, folders: Iterable[PathLike]) -> None:
        """
        Add rows into the database additively.

        This method accepts a folders iterable and adds them to the
        existing database. It serves to avoid re-crawling folders that had
        already been selected previously.

        Args:
            folders: Iterable of folders to be added
        """
        if not folders:
            return

        with self.crawler_class() as crawler:
            for folder in folders:
                inserted = 0
                rows = self.generate_rows(folder, crawler)
                batches = self.generator_of_batches(rows, self.batch_size)
                for batch in batches:
                    inserted += self.backend.insert_rows(batch)
                logger.debug(
                    f"""
                    Crawl done: rom folder {folder} {inserted} were inserted.
                    """
                )

    @staticmethod
    def generate_rows(folder, crawler) -> Generator[ImageRow, Any, None]:
        for file_entry in crawler.crawl(folders=folder):
            yield ImageRow.from_file_entry(file_entry)

    @staticmethod
    def generator_of_batches(
        rows: Generator[ImageRow, None, None], batch_size: int
    ) -> Generator[Generator[ImageRow, None, None], None, None]:
        """
        Yield generators of up to batch_size rows.
        Each batch is itself a generator, not a list.
        """

        def make_batch(
            initial_row: ImageRow,
            remaining_rows: Generator[ImageRow, None, None],
        ):
            """Yield first_row + up to batch_size-1 from remaining_rows"""
            count = 0
            yield initial_row
            count += 1
            for row in remaining_rows:
                yield row
                count += 1
                if count >= batch_size:
                    break

        # Materialize the rows_generator as an iterator
        rows_iter = iter(rows)
        while True:
            try:
                first_row = next(rows_iter)
            except StopIteration:
                break
            # Yields mini generators of size: batch_size
            yield make_batch(first_row, rows_iter)

    def remove_rows(self, folders: Iterable[PathLike]):
        """
        Remove rows of paths under given directory from database

        This method removes all rows with paths under the provided parent
        directories.

        Args:
            parent_folders list[str]: Parent directories to be removed
        """
        self.backend.remove_rows(folders)

    def update_seen(self, folders: Iterable[PathLike]):
        # TODO to be implemented once async loading is possible
        self.backend.mark_seen(folders)


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


class Loader:
    """Read all paths in a SQLite database, filtering and sorting them.

    Attributes:
        :ivar database: Connection to the SQLite database
    """

    def __init__(self, db_path=":memory:"):
        self.database = sqlite3.connect(db_path)

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
