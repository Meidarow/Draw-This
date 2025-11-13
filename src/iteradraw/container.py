"""
Dependency injection container for Iteradraw.

Defines the DI injection blocks for components of the application,
to be called by the boostrapper at app initialization.
"""

from iteradraw.application.commands.folder_commands import (
    AddFolderCommand,
    RemoveFolderCommand,
    RenameFolderSetCommand,
    AddFolderSetCommand,
    SetFolderEnabledCommand,
    SetAllFoldersEnabledCommand,
    MoveFolderBetweenFolderSetsCommand,
    DeleteFolderSetCommand,
)
from iteradraw.application.handlers.folder_handlers import (
    AddFolderCommandHandler,
    RemoveFolderCommandHandler,
    RenameFolderSetCommandHandler,
    AddFolderSetCommandHandler,
    SetFolderEnabledCommandHandler,
    SetAllFoldersEnabledCommandHandler,
    MoveFolderBetweenFolderSetsCommandHandler,
    DeleteFolderSetCommandHandler,
)
from iteradraw.domain.repositories.folder_repository import FolderRepository
from iteradraw.infrastructure.buses.command_bus import CommandBus
from iteradraw.infrastructure.buses.event_bus import EventBus
from iteradraw.infrastructure.persistence.sqlite3_domain_database import (
    SQLite3DomainDatabase,
)
from iteradraw.infrastructure.services import UUIDGenerator


class DependencyContainer:
    def __init__(self):
        self.container = None

    def build(self):
        # TODO if methods stay small -> unify them in build
        self._build_container()
        self._install_modules()

    def _build_container(self):
        self.container = {
            "event_bus": EventBus(),
            "command_bus": CommandBus(),
            "folder_repo": FolderRepository(
                persistence=SQLite3DomainDatabase(db_path="")
            ),
        }

    def _install_modules(self):
        CommandAssignment().register(self.container)


class CommandAssignment:
    def __init__(self):
        self.folder_repo = None
        self.command_bus = None
        self.event_bus = None

    def register(self, container):
        self.event_bus = container["event_bus"]
        self.command_bus = container["command_bus"]
        self.folder_repo = container["folder_repo"]
        self._assign_folder_command_handlers()
        self._assign_timer_command_handlers()

    def _assign_folder_command_handlers(self):
        add_folder_handler = AddFolderCommandHandler(
            folder_repo=self.folder_repo, event_bus=self.event_bus
        )
        self.command_bus.register(
            command_type=AddFolderCommand,
            handler=add_folder_handler.handle,
        )

        remove_folder_handler = RemoveFolderCommandHandler(
            folder_repo=self.folder_repo, event_bus=self.event_bus
        )
        self.command_bus.register(
            command_type=RemoveFolderCommand,
            handler=remove_folder_handler.handle,
        )

        rename_folderset_handler = RenameFolderSetCommandHandler(
            folder_repo=self.folder_repo, event_bus=self.event_bus
        )
        self.command_bus.register(
            command_type=RenameFolderSetCommand,
            handler=rename_folderset_handler.handle,
        )

        add_folderset_handler = AddFolderSetCommandHandler(
            folder_repo=self.folder_repo,
            event_bus=self.event_bus,
            id_generator=UUIDGenerator(),
        )
        self.command_bus.register(
            command_type=AddFolderSetCommand,
            handler=add_folderset_handler.handle,
        )

        delete_folderset_handler = DeleteFolderSetCommandHandler(
            folder_repo=self.folder_repo, event_bus=self.event_bus
        )
        self.command_bus.register(
            command_type=DeleteFolderSetCommand,
            handler=delete_folderset_handler.handle,
        )

        set_folder_enabled_handler = SetFolderEnabledCommandHandler(
            folder_repo=self.folder_repo, event_bus=self.event_bus
        )
        self.command_bus.register(
            command_type=SetFolderEnabledCommand,
            handler=set_folder_enabled_handler.handle,
        )

        set_all_folders_enabled_handler = SetAllFoldersEnabledCommandHandler(
            folder_repo=self.folder_repo, event_bus=self.event_bus
        )
        self.command_bus.register(
            command_type=SetAllFoldersEnabledCommand,
            handler=set_all_folders_enabled_handler.handle,
        )

        move_folder_between_foldersets_handler = (
            MoveFolderBetweenFolderSetsCommandHandler(
                folder_repo=self.folder_repo, event_bus=self.event_bus
            )
        )
        self.command_bus.register(
            command_type=MoveFolderBetweenFolderSetsCommand,
            handler=move_folder_between_foldersets_handler.handle,
        )

    def _assign_timer_command_handlers(self):
        ...
