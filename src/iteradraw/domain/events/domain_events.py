from dataclasses import dataclass

from iteradraw.domain.events.interfaces import Event


@dataclass(frozen=True)
class FolderAdded(Event):
    ...


@dataclass(frozen=True)
class FolderRemoved(Event):
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
