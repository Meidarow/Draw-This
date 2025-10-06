from pathlib import Path
from typing import (
    runtime_checkable,
    Protocol,
    Iterator,
)


@runtime_checkable
class StatLike(Protocol):
    st_mtime: float
    st_ino: int
    st_dev: int


@runtime_checkable
class DirEntryLike(Protocol):
    path: str

    def is_dir(self) -> bool:
        ...

    def is_symlink(self) -> bool:
        ...

    def stat(self) -> "StatLike":
        ...


@runtime_checkable
class DirectoryScanner(Protocol):
    def __call__(self, directory: str | Path) -> Iterator["DirEntryLike"]:
        ...


@runtime_checkable
class FilterLike(Protocol):
    def add(self, item: str) -> None:
        ...

    def __contains__(self, item: str) -> bool:
        ...
