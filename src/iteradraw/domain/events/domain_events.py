from dataclasses import dataclass

from iteradraw.domain.events.interfaces import Event
from iteradraw.domain.models.folder import FolderSet


@dataclass(frozen=True)
class FolderAdded(Event):
    ...


@dataclass(frozen=True)
class FolderRemoved(Event):
    ...


@dataclass(frozen=True)
class FolderSetAdded(Event):
    folderset: FolderSet


@dataclass(frozen=True)
class FolderSetRemoved(Event):
    ...


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
