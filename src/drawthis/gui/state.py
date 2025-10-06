from dataclasses import dataclass, field

"""
This module holds the definitions for all dataclasses used for state-keeping
in the model.

Dataclasses:
-FolderSet: Set of folder, enabled (tuple[str,bool]) pairs
-TimerSet: Set of timers (list[int])
-Session: Set of all parameters in a Draw-This session
"""


@dataclass
class FolderSet:
    """
    Wrapper for a set of folders

    Guarantees:
    - Folders are always unique (no duplicates), keyed by folder name
    """

    _folders: dict[str, bool] = field(default_factory=dict)

    @classmethod
    def from_pairs(cls, pairs: list[tuple[str, bool]]) -> "FolderSet":
        """Factory for FolderSet, from (path, enabled) pairs"""
        fs = cls()
        for path, enabled in pairs:
            fs.add(path, enabled)
        return fs

    def add(self, path: str, enabled: bool = True) -> None:
        """Add a folder with optional enabled state."""
        self._folders[path] = enabled

    def remove(self, path: str) -> None:
        """Remove a folder."""
        self._folders.pop(path, None)

    def toggle(self, path: str) -> None:
        """Flip enabled/disabled state for a folder."""
        if path in self._folders:
            self._folders[path] = not self._folders[path]

    def enable(self, path: str) -> None:
        """Enable a folder explicitly."""
        self._folders[path] = True

    def disable(self, path: str) -> None:
        """Disable a folder explicitly."""
        self._folders[path] = False

    @property
    def enabled(self) -> list[str]:
        """Return only enabled folders."""
        return [f for f, e in self._folders.items() if e]

    @property
    def disabled(self) -> list[str]:
        """Return only disabled folders."""
        return [f for f, e in self._folders.items() if not e]

    @property
    def all(self) -> dict[str, bool]:
        """Raw view of all folders and states."""
        return dict(self._folders)

    def copy(self) -> "FolderSet":
        """Return identical copy of self"""
        return FolderSet(_folders=self.all)


@dataclass
class TimerSet:
    """
    Wrapper for a set of timers

    Guarantees:
    - List is always sorted
    - No duplicate timers can be inserted
    """

    _timers: list[int] = field(default_factory=list)

    @classmethod
    def from_list(cls, timers: list[int]) -> "TimerSet":
        """Factory for TimerSet from list of timers"""
        ts = cls()
        for timer in timers:
            ts.add(timer)
        return ts

    def add(self, timer: int) -> None:
        """Add a new timer if not already present, then sort timer list"""
        if timer in self._timers:
            return
        self._timers.append(timer)
        self._timers = sorted(self._timers)

    def remove(self, timer: int) -> None:
        """Remove a timer"""
        self._timers.remove(timer)

    @property
    def all(self) -> list[int]:
        """Raw view of all timers"""
        return list(self._timers)

    def copy(self) -> "TimerSet":
        """Return identical copy of self"""
        return TimerSet(_timers=self.all)


@dataclass
class Session:
    timers: TimerSet = field(default_factory=TimerSet)
    folders: FolderSet = field(default_factory=FolderSet)
    selected_timer: int = 0
    geometry: tuple = None
    is_running: bool = False

    @classmethod
    def from_dict(cls, session_dict: dict) -> "Session":
        return cls(
            timers=TimerSet.from_list(session_dict.get("timers", [])),
            folders=FolderSet.from_pairs(
                list(session_dict.get("folders", {}).items())
            ),
            selected_timer=session_dict.get("selected_timer", 0),
        )

    def to_dict(self) -> dict:
        session_dict = {
            "timers": self.timers.all,
            "folders": self.folders.all,
            "selected_timer": self.selected_timer,
        }
        return session_dict

    def copy(self) -> "Session":
        return Session(
            timers=self.timers.copy(),
            folders=self.folders.copy(),
            selected_timer=self.selected_timer,
        )
