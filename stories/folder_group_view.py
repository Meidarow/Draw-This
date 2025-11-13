import sys
import uuid
from uuid import UUID

from PySide6.QtWidgets import QApplication, QMainWindow

from iteradraw.domain.models.folder import Folder, FolderSet
from iteradraw.presentation.pyside.viewmodels.folder_group_viewmodel import (
    FolderGroupViewModel,
)
from iteradraw.presentation.pyside.views.folder_views import FolderGroupView
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
    real_path = "/mnt/Storage/Art/Resources/Animals/ANM-0001.jpg"  # to test
    # open folder
    folders[real_path] = Folder(path=real_path, enabled=True)
    return FolderSet(uuid=folderset_id, display_name=name, _folders=folders)


def main():
    # 1. Set up the Qt Application
    app = QApplication(sys.argv)

    try:
        with open("/home/study/Draw-This/assets/main.qss", "r") as f:
            qss_string = f.read()
            app.setStyleSheet(qss_string)
    except FileNotFoundError:
        print("WARNING: main.qss not found. Using default styles.")

    # 2. Instantiate your REAL ViewModel with FAKE buses
    vm = FolderGroupViewModel(
        command_bus=MockCommandBus(),
        event_bus=MockEventBus(),
        # You'll also need a mock query_bus or repo
        # to handle the initial data load
    )

    # 3. Instantiate your REAL View
    #    (You'll need to refactor its __init__ to just take the VM)
    view = FolderGroupView(viewmodel=vm)

    # 4. Manually load mock data into the VM
    #    (This replaces the query bus for the showcase)
    folderset_id = uuid.uuid4()
    mock_data = get_mock_folderset(
        name="Figures", num_folders=10, folderset_id=folderset_id
    )
    vm.populate(mock_data)  # Or vm.load_data(mock_data), whatever you call it

    # 5. Create a window and show your component
    window = MainWindow()
    window.setCentralWidget(view)
    window.show()

    # Run the app
    sys.exit(app.exec())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Showcase: FolderGroupView")
        self.resize(960, 540)


if __name__ == "__main__":
    main()
