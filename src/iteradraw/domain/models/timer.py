from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# =============================================================================
# Settings - Extra slideshow/Idle domain
# =============================================================================

"""
This module holds the definitions for all dataclasses used by the
AppSettingsService.

Dataclasses:
-AppSettings: Set of all parameters outside a Draw-This resources.
-FolderSet: Wrapper for folders with enabled/disabled flag.
-TimerSet: Wrapper for timers.

Enums:
-APPSETTINGS.FIELDS: Reflects fields of AppSettings, centralizing refactors
-APPSETTINGS.DEFAULTS: Defines sane defaults for all fields of AppSettings
"""


@dataclass(frozen=True)
class TimerSet(Model):
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
