"""
Dependency injection container for Iteradraw.

Defines the DI injection blocks for components of the application,
to be called by the boostrapper at app initialization.
"""

from iteradraw.application.commands.folder_commands import (
    AddFolderCommand,
    RemoveFolderCommand,
    RenameFolderSetCommand,
)
from iteradraw.application.handlers.folder_handlers import (
    AddFolderCommandHandler,
    RemoveFolderCommandHandler,
    RenameFolderSetCommandHandler,
)
from iteradraw.domain.repositories.folder_repository import FolderRepository
from iteradraw.infrastructure.buses.command_bus import CommandBus
from iteradraw.infrastructure.buses.event_bus import EventBus
from iteradraw.infrastructure.persistence.sqlite3_domain_database import (
    SQLite3DomainDatabase,
)


class Container:
    # TODO if methods stay small -> unify them in build
    def __init__(self):
        self.container = None

    def build(self):
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
            handler=add_folder_handler.add_folder,
        )

        remove_folder_handler = RemoveFolderCommandHandler(
            folder_repo=self.folder_repo, event_bus=self.event_bus
        )
        self.command_bus.register(
            command_type=RemoveFolderCommand,
            handler=remove_folder_handler.remove_folder,
        )

        rename_folderset_handler = RenameFolderSetCommandHandler(
            folder_repo=self.folder_repo, event_bus=self.event_bus
        )
        self.command_bus.register(
            command_type=RenameFolderSetCommand,
            handler=rename_folderset_handler.rename_folderset,
        )

        add_folderset_handler = AddFolderSetCommandHandler(
            folder_repo=self.folder_repo, event_bus=self.event_bus
        )
        self.command_bus.register(
            command_type=AddFolderSetCommand,
            handler=add_folderset_handler.add_folderset,
        )

        remove_folderset_handler = RemoveFolderSetCommandHandler(
            folder_repo=self.folder_repo, event_bus=self.event_bus
        )
        self.command_bus.register(
            command_type=RemoveFolderSetCommand,
            handler=remove_folderset_handler.remove_folderset,
        )

    def _assign_timer_command_handlers(self): ...
