from dataclasses import dataclass


@dataclass(frozen=True)
class AddTimerCommand:
    duration: int


@dataclass(frozen=True)
class RemoveTimerCommand:
    duration: int
