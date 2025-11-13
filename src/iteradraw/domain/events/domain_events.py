from dataclasses import dataclass
from uuid import UUID

from iteradraw.domain.events.interfaces import Event
from iteradraw.domain.models.folder import FolderSet


@dataclass(frozen=True)
class FolderAdded(Event):
    folderset_id: UUID
    folder_path: str
    enabled: bool


@dataclass(frozen=True)
class FolderRemoved(Event):
    folderset_id: UUID
    folder_path: str


@dataclass(frozen=True)
class FolderSetAdded(Event):
    folderset: FolderSet


@dataclass(frozen=True)
class FolderSetRemoved(Event):
    folderset_id: UUID


class FolderSetRenamed(Event):
    folderset_id: UUID
    new_name: str


@dataclass(frozen=True)
class TimerAdded(Event):
    ...


@dataclass(frozen=True)
class TimerRemoved(Event):
    ...


@dataclass(frozen=True)
class SessionVerified(Event):
    ...


@dataclass(frozen=True)
class SessionStarted(Event):
    ...


@dataclass(frozen=True)
class SessionFailed(Event):
    ...
