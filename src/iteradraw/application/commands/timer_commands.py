from dataclasses import dataclass

from iteradraw.application.commands.interfaces import Command


@dataclass(frozen=True)
class AddTimerCommand(Command):
    duration: int


@dataclass(frozen=True)
class RemoveTimerCommand(Command):
    duration: int
