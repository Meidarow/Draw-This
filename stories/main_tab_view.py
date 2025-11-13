import sys
import uuid
from uuid import UUID

from PySide6.QtWidgets import QApplication

# 2. Import the REAL commands and events your view uses
from iteradraw.application.commands.folder_commands import AddFolderSetCommand
from iteradraw.domain.events.domain_events import FolderSetAdded
from iteradraw.domain.models.folder import Folder, FolderSet

# 1. Import your REAL buses
from iteradraw.infrastructure.buses.command_bus import CommandBus
from iteradraw.infrastructure.buses.event_bus import EventBus

# 3. Import your REAL window
from iteradraw.presentation.pyside.views.window_views import MainWindow


# stories.mocks is no longer needed


# --- This is your "clean-room" setup ---


def get_mock_folderset(
    name: str, num_folders: int, folderset_id: UUID
) -> FolderSet:
    """Creates fake data for the VM."""
    folders = {}
    for i in range(num_folders):
        path = f"/path/to/folder_{i}"
        folders[path] = Folder(path=path, enabled=(i % 2 == 0))
    return FolderSet(uuid=folderset_id, display_name=name, folders=folders)


def main():
    # Set up the Qt Application
    app = QApplication(sys.argv)

    try:
        with open("/home/study/Draw-This/assets/main.qss", "r") as f:
            qss_string = f.read()
            app.setStyleSheet(qss_string)
    except FileNotFoundError:
        print("WARNING: main.qss not found. Using default styles.")

    # === THIS IS THE "BEST WAY" ===

    # 1. Create REAL, functional buses
    command_bus = CommandBus()
    event_bus = EventBus()

    # 2. Create a FAKE, LOCAL handler
    def fake_add_folderset_handler(command: AddFolderSetCommand):
        """
        This fake handler simulates the "Unit of Work"
        (get, modify, save, publish) without a database.
        """
        print("STORY: CommandBus received: {command.display_name}")

        # Create the fake data the UI expects
        new_id = uuid.uuid4()
        mock_set = get_mock_folderset(
            name=command.display_name,
            num_folders=5,  # Or 0, or whatever you want
            folderset_id=new_id,
        )

        # "Publish" the event the FolderPanelView is waiting for
        print("STORY: EventBus publishing: FolderSetAdded")
        evt = FolderSetAdded(folderset=mock_set)
        event_bus.publish(evt)

    # 3. Register the FAKE handler to the REAL bus
    command_bus.register(AddFolderSetCommand, fake_add_folderset_handler)

    # (You can add more fake handlers here for Delete, Rename, etc.)

    # 4. Inject the REAL (but locally-wired) buses
    window = MainWindow(
        command_bus=command_bus,
        event_bus=event_bus,
    )
    window.show()

    # Run the app
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
