import sys

from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSplitter,
    QMainWindow,
    QTabWidget,
    QApplication,
)

from iteradraw.presentation.pyside.views.folder_views import FolderPanelView
from iteradraw.presentation.pyside.views.sidebar_views import SidePanelView


class MainWindow(QMainWindow):
    def __init__(self, command_bus, event_bus):
        super().__init__()
        self.setWindowTitle("Showcase: FolderGroupView")
        self.resize(960, 540)
        tabs = QTabWidget()
        main_tab = MainTab(command_bus=command_bus, event_bus=event_bus)
        settings_tab = SettingsTab()

        tabs.addTab(main_tab, "Slideshow")
        tabs.addTab(settings_tab, "⚙")
        self.setCentralWidget(tabs)

    def initialize(self):
        ...


class MainTab(QWidget):
    """
    View of the primary tab of Iteradraw.

    Coordinates the segments of the GUI and emits signals.

    Core Segments:
      - Folder Segment: Allows user to view folder/foldergroups, perform
      CRUD ops on them and select/deselect them.
      - Timer Segment: Allows user to add/select timers.
      - Trigger Segment: Presents buttons for the user to trigger app
      behaviors.

    Does NOT handle any data, only UI elements. Data handling is delegated
    to each apropriate data-bound component's viewmodel.
    """

    def __init__(self, command_bus, event_bus):
        super().__init__()
        horizontal_splitter = QSplitter(Qt.Orientation.Horizontal)

        folder_panel = FolderPanelView(
            command_bus=command_bus, event_bus=event_bus
        )
        sidebar_panel = SidePanelView()

        horizontal_splitter.addWidget(folder_panel)
        horizontal_splitter.addWidget(sidebar_panel)
        horizontal_splitter.setStretchFactor(0, 12)
        horizontal_splitter.setStretchFactor(1, 1)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(horizontal_splitter)


class SettingsTab(QWidget):
    """
    Secondary settings tab for Iteradraw.

    Presents a series of settings that can be altered to the user's preference.

    Core Segments:

    """

    ...


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
