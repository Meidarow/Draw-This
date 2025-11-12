import sys
from uuid import UUID

from PySide6.QtWidgets import QApplication

from iteradraw.domain.models.folder import Folder, FolderSet
from iteradraw.presentation.pyside.views.window_views import MainWindow
from stories.mocks import MockCommandBus, MockEventBus


# 1. Import your REAL components

# --- This is your "clean-room" setup ---


def get_mock_folderset(
    name: str, num_folders: int, folderset_id: UUID
) -> FolderSet:
    """Creates fake data for the VM."""
    folders = {}
    for i in range(num_folders):
        path = f"/path/to/folder_{i}"
        folders[path] = Folder(path=path, enabled=(i % 2 == 0))
    return FolderSet(uuid=folderset_id, display_name=name, _folders=folders)


def main():
    # Set up the Qt Application
    app = QApplication(sys.argv)

    try:
        with open("/home/study/Draw-This/assets/main.qss", "r") as f:
            qss_string = f.read()
            app.setStyleSheet(qss_string)
    except FileNotFoundError:
        print("WARNING: main.qss not found. Using default styles.")

    # Create a window and show your component
    window = MainWindow(
        command_bus=MockCommandBus(),
        event_bus=MockEventBus(),
    )
    window.show()

    # Run the app
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
