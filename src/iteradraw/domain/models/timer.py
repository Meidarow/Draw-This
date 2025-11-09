from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

"""
This module holds the definitions for all dataclasses used by the
AppSettingsService.

Classes:
    TimerSet: Wrapper for timers.

Usage:
"""


@dataclass(frozen=True)
class TimerSet:
    """
    Wrapper for a set of timers

    Guarantees:
    - List is always sorted
    - No duplicate timers can be inserted
    """

    _timers: list[int] = field(default_factory=list)

    def add(self, timer: int) -> "TimerSet":
        """Add a new timer if not already present, then sort timer list"""
        if timer in self._timers:
            return self
        timers = self._timers.copy()
        timers.append(timer)
        timers = sorted(timers)
        return replace(self, _timers=timers)

    def remove(self, timer: int) -> "TimerSet":
        """Remove a timer"""
        timers = self._timers.copy()
        timers.remove(timer)
        return replace(self, _timers=timers)

    @property
    def all(self) -> list[int]:
        """Raw view of all timers"""
        return list(self._timers)
