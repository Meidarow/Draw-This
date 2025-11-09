"""
Repository layer for persistence of domain models such as FolderSet, TimerSet,
and aggregate roots like Session.

Repositories act as the boundary between the domain/application layers and the
underlying persistence mechanisms (e.g. JSON, SQLite). They expose operations
in domain terms — load, save, update — without leaking any storage details.

Each repository encapsulates its respective model’s persistence behavior,
providing better modularity and Separation of Concerns.

Classes:
    FolderRepository:  Manages persistence for FolderSet.
    TimerRepository:   Manages persistence for TimerSet.
    SessionRepository: Coordinates FolderRepository and TimerRepository
                       to persist or reconstruct Session aggregates.

Usage:
    folder_repo = FolderRepository()
    last_folder_set = folder_repo.load()
    ...
    folder_repo.save(modified_folder_set)
"""

from enum import StrEnum
from typing import Callable

from iteradraw.domain.models.folder import FolderSet, Folder
from iteradraw.domain.models.session import Session
from iteradraw.domain.models.timer import TimerSet
from iteradraw.domain.repositories.interfaces import Persistence
from iteradraw.infrastructure.persistence.json_persistence import (
    JsonPersistence,
)


class RepositoryNamespaces(StrEnum):
    Folders = "folders"
    Timers = "timers"
    Session = "session"


class FolderRepository:
    """
    Repository for FolderSet domain objects.

    Facilitates persistence operations for the FolderSet model by
    abstracting backend implementations and providing (de-)serialization
    methods. Allows for backend injection, as long as implementation follows
    the Persistence protocol.

    Handles only FolderSets since an individual Folder is not meant to exist
    outside a folder set.
    """

    def __init__(
        self, persistence: Persistence, platform_config_dir: Callable
    ):
        self.persistence = persistence or JsonPersistence(
            namespace=RepositoryNamespaces.Folders,
            file_name="session.json",
            settings_dir_path=platform_config_dir(),
            on_read_error=None,
            on_write_error=None,
        )

    def get(self, folder_id: str) -> FolderSet: ...

    def get_all(self) -> list[FolderSet]: ...

    def save(self, data: list[FolderSet]): ...

    @staticmethod
    def _folderset_from_dict(data):
        folders = data["folders"]
        name = ""
        if not folders:
            raise ValueError("No valid folders given")
        return FolderSet(
            name=name,
            _folders={fd: Folder(path=fd, enabled=en) for fd, en in folders},
        )

    @staticmethod
    def _folderset_to_dict(folderset) -> list[dict[str, bool]]:
        """Raw view of all folders and states."""
        return [{folder.path: folder.enabled} for folder in folderset.all]


class TimerRepository:
    """
    Repository for TimerSet domain objects.

    Facilitates persistence operations for the TimerSet model by
    abstracting backend implementations and providing (de-)serialization
    methods. Allows for backend injection, as long as implementation
    follows the Persistence protocol.
    """

    def __init__(
        self, persistence: Persistence, platform_config_dir: Callable
    ):
        self.persistence = persistence or JsonPersistence(
            namespace=RepositoryNamespaces.Timers,
            file_name="session.json",
            settings_dir_path=platform_config_dir(),
            on_read_error=None,
            on_write_error=None,
        )

    def get_all(self) -> list[TimerSet]: ...

    def save(self, data: list[TimerSet]): ...

    @staticmethod
    def _from_list(timers: list[int]) -> TimerSet:
        """Factory for TimerSet from list of timers"""
        ts = TimerSet()
        for timer in timers:
            ts.add(timer)
        return ts


class SessionRepository:
    def __init__(
        self, persistence: Persistence, platform_config_dir: Callable
    ):
        self.persistence = persistence or JsonPersistence(
            namespace=RepositoryNamespaces.Session,
            file_name="session.json",
            settings_dir_path=platform_config_dir(),
            on_read_error=None,
            on_write_error=None,
        )

    def get(self) -> Session: ...

    def save(self, data: Session): ...

    @staticmethod
    def from_dict(d: dict) -> "Session":
        """
        This allows for automatic synchronicity between the SessionFields
        and the Session constructor/converter methods.
        Args:
            d: input dict with values to be inserted into Session

        Returns:
            A Session instance with fields matching SessionFields. Always
            instantiated with sane defaults for missing values.
        """
        kwargs = {}
        for field in Session.Fields:
            attribute_name = field
            kwargs[attribute_name] = d.get(
                field, getattr(Session, attribute_name)
            )
        return Session(**kwargs)

    @staticmethod
    def to_dict() -> dict:
        """
        This allows for automatic synchronicity between the SessionFields
        and the Session constructor/converter methods.

        Returns:
            A Dict with keys matching SessionFields.
        """
        return {field: getattr(Session, field) for field in Session.Fields}
