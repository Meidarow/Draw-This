from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from iteradraw.application.commands.interfaces import Command

"""
Commands
"""


@dataclass(frozen=True)
class AddFolderCommand(Command):
    folderset_id: UUID
    folder_path: str
    enabled: bool


@dataclass(frozen=True)
class RemoveFolderCommand(Command):
    folderset_id: UUID
    folder_path: str


@dataclass(frozen=True)
class RenameFolderSetCommand(Command):
    folderset_id: UUID
    new_folderset_name: str


@dataclass(frozen=True)
class AddFolderSetCommand(Command):
    display_name: Optional[str]


@dataclass(frozen=True)
class DeleteFolderSetCommand(Command):
    folderset_id: UUID


@dataclass(frozen=True)
class MoveFolderBetweenFolderSetsCommand(Command):
    origin_folderset_id: UUID
    destination_folderset_id: UUID
    folder_path: str


@dataclass(frozen=True)
class SetFolderEnabledCommand(Command):
    folderset_id: UUID
    folder_path: str
    target_enabled: bool


@dataclass(frozen=True)
class SetAllFoldersEnabledCommand(Command):
    folderset_id: UUID
    target_enabled: bool
