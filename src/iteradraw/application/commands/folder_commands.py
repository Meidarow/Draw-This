from dataclasses import dataclass

from iteradraw.application.commands.interfaces import Command

"""
Commands
"""


@dataclass(frozen=True)
class AddFolderCommand(Command):
    folderset_name: str
    folder_path: str
    enabled: bool


@dataclass(frozen=True)
class RemoveFolderCommand(Command):
    folderset_name: str
    folder_path: str


@dataclass(frozen=True)
class RenameFolderSetCommand(Command):
    folderset_name: str
    new_folderset_name: str


@dataclass(frozen=True)
class DeleteFolderSetCommand(Command):
    folderset_name: str


@dataclass(frozen=True)
class MoveFolderBetweenFolderSetsCommand(Command):
    origin_folderset_name: str
    destination_folderset_name: str
    folder_path: str
