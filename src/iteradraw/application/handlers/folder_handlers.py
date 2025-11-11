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
    AddFolderSetCommand,
)
from iteradraw.application.handlers.interfaces import IdGenerator
from iteradraw.domain.events.domain_events import (
    FolderAdded,
    FolderRemoved,
    FolderSetAdded,
)
from iteradraw.domain.models.folder import FolderSet
from iteradraw.domain.repositories.folder_repository import FolderRepository
from iteradraw.infrastructure.buses.event_bus import EventBus


class AddFolderCommandHandler:
    def __init__(self, folder_repo: FolderRepository, event_bus: EventBus):
        self.folder_repo = folder_repo
        self.event_bus = event_bus

    def add_folder(self, command: AddFolderCommand):
        old_folderset = self.folder_repo.get(command.folderset_id)
        new_folderset = old_folderset.add(command.folder_path, command.enabled)
        self.folder_repo.save(folderset=new_folderset)
        evt = FolderAdded(
            folderset_id=command.folderset_id, folder_path=command.folder_path
        )
        self.event_bus.publish(evt)


class RemoveFolderCommandHandler:
    def __init__(self, folder_repo: FolderRepository, event_bus: EventBus):
        self.folder_repo = folder_repo
        self.event_bus = event_bus

    def remove_folder(self, command: RemoveFolderCommand):
        old_folderset = self.folder_repo.get(command.folderset_id)
        new_folderset = old_folderset.remove(command.folder_path)
        self.folder_repo.save(folderset=new_folderset)
        evt = FolderRemoved(folder_path=command.folder_path)
        self.event_bus.publish(evt)


class RenameFolderSetCommandHandler:
    def __init__(
        self,
        folder_repo: FolderRepository,
        event_bus: EventBus,
    ):
        self.folder_repo = folder_repo
        self.event_bus = event_bus

    def rename_folderset(self, command: RenameFolderSetCommand):
        old_folderset = self.folder_repo.get(command.folderset_id)
        new_folderset = old_folderset.rename(command.new_folderset_name)
        self.folder_repo.save(folderset=new_folderset)


class AddFolderSetCommandHandler:
    def __init__(
        self,
        folder_repo: FolderRepository,
        event_bus: EventBus,
        id_generator: IdGenerator,
    ):
        self.folder_repo = folder_repo
        self.event_bus = event_bus
        self.id_generator = id_generator

    def handle(self, command: AddFolderSetCommand):
        new_folderset_id = self.id_generator.generate()
        new_folderset = FolderSet(
            uuid=new_folderset_id, display_name=command.display_name
        )
        self.folder_repo.save(folderset=new_folderset)
        evt = FolderSetAdded(folderset=new_folderset)
        self.event_bus.publish(evt)


class DeleteFolderSetCommandHandler:
    def __init__(self, folder_repo: FolderRepository, event_bus: EventBus):
        self.folder_repo = folder_repo
        self.event_bus = event_bus

    def remove_folder(self, command: DeleteFolderSetCommand):
        old_folderset = self.folder_repo.get(command.folderset_id)
        self.folder_repo.save(folderset=new_folderset)


# TODO repo delete method is TBD


class MoveFolderBetweenFolderSetsCommandHandler:
    """
    Careful here, this requires changing both foldersets AFTER verifying if
    the target FS can receive the folder, that is, doesn't already have it.
    """

    ...
