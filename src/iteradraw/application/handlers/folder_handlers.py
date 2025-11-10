"""
Handlers for all Folder and FolderSet based operations in IteraDraw.

Classes:
    AddFolderCommandHandler
    RemoveFolderCommandHandler
    RenameFolderSetCommandHandler
    AddFolderSetCommandHandler
    RemoveFolderSetCommandHandler
    MoveFolderBetweenFolderSetsCommandHandler
    ChangeFolderEnabledCommandHandler
    ChangeAllFoldersEnabledCommandHandler
"""

from iteradraw.application.commands.folder_commands import (
    AddFolderCommand,
    RemoveFolderCommand,
    RenameFolderSetCommand,
    DeleteFolderSetCommand,
)
from iteradraw.domain.repositories.folder_repository import FolderRepository


class AddFolderCommandHandler:
    def __init__(self, folder_repo: FolderRepository):
        self.folder_repo = folder_repo

    def add_folder(self, command: AddFolderCommand):
        old_folderset = self.folder_repo.get(command.folderset_name)
        new_folderset = old_folderset.add(command.folder_path, command.enabled)
        self.folder_repo.save(folderset=new_folderset)


class RemoveFolderCommandHandler:
    def __init__(self, folder_repo: FolderRepository):
        self.folder_repo = folder_repo

    def remove_folder(self, command: RemoveFolderCommand):
        old_folderset = self.folder_repo.get(command.folderset_name)
        new_folderset = old_folderset.remove(command.folder_path)
        self.folder_repo.save(folderset=new_folderset)


class RenameFolderSetCommandHandler:
    def __init__(self, folder_repo: FolderRepository):
        self.folder_repo = folder_repo

    def rename_folder(self, command: RenameFolderSetCommand):
        old_folderset = self.folder_repo.get(command.folderset_name)
        new_folderset = old_folderset.rename(command.new_folderset_name)
        self.folder_repo.save(folderset=new_folderset)


# TODO FolderSet.rename method is TBD


class DeleteFolderSetCommandHandler:
    def __init__(self, folder_repo: FolderRepository):
        self.folder_repo = folder_repo

    def remove_folder(self, command: DeleteFolderSetCommand):
        old_folderset = self.folder_repo.get(command.folderset_name)
        self.folder_repo.save(folderset=new_folderset)


# TODO repo delete method is TBD


class MoveFolderBetweenFolderSetsCommandHandler: ...
