import threading
from pathlib import Path
from typing import (
    Iterable,
    Generator,
    Any,
)

from drawthis.core.events.logger import logger
from drawthis.core.models.session.dataclasses import (
    ImageRow,
)
from drawthis.persistence.session.sqlite3_backend import SQLite3Backend
from drawthis.services.session.crawler import Crawler

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


class DatabaseManager:
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
        self.batch_size = batch_size or 5000

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
        self.backend.commit()

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

    def load_all_rows(self):
        """
        Return all database entries.

        Legacy Loader soluction simply adapted into the new framework.
        TODO remove once async loader has been implemented
        """
        return self.backend.load_whole_database()
