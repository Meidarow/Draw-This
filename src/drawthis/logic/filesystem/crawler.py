import os
import queue
from pathlib import Path
from typing import (
    Iterable,
    Callable,
    Generator,
    Optional,
)

from pybloom_live import BloomFilter

from drawthis.logic.core.dataclasses import FileEntry
from drawthis.logic.core.protocols import (
    DirectoryScanner,
    FilterLike,
)
from drawthis.utils.logger import logger

PathLike = str | Path
FolderInput = PathLike | Iterable[PathLike]


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
        dir_access_fn: "DirectoryScanner" = None,
        bloom_filter: Optional["FilterLike"] = None,
    ):
        self.on_start = on_start
        self.on_end = on_end
        self.on_skip = on_skip
        self.directory_queue: queue.Queue[str] = queue.Queue()
        self.dir_access = dir_access_fn or os.scandir
        self.filter = bloom_filter
        self._files_skipped = 0

    def __enter__(self):
        self.reset_state()
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
        bloom_filter: Optional["FilterLike"] = None,
        bloom_filter_cap: int = 100000,
        bloom_filter_error_rate: float = 0.001,
    ):
        """Reset Crawler for re-use, also resets skipped files counter"""
        self._files_skipped = 0
        self.clear_queue()
        self.filter = bloom_filter or BloomFilter(
            capacity=bloom_filter_cap, error_rate=bloom_filter_error_rate
        )

    def crawl(self, folders: FolderInput) -> Iterable["FileEntry"]:
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
    ) -> Generator["FileEntry", None, None]:
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
