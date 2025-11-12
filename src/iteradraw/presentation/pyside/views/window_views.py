from PySide6.QtGui import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSplitter,
    QMainWindow,
    QTabWidget,
    QFileDialog,
)

from iteradraw.presentation.pyside.views.folder_views import FolderPanelView
from iteradraw.presentation.pyside.views.sidebar_views import SidePanelView


class MainWindow(QMainWindow):
    """
    Top level window of Iteradraw.

    Singular window created by Iteradraw, except dialog windows.

    Core Tabs:
        - MainTab: Slideshow parameter and start-up tab.
        - SettingsTab: User preference config window.
        - Streak (TBD): Tracks user study time/streak.

    Methods:
        - initialize(): Initial boot-up and data load for the app.
    """

    def __init__(self, command_bus, event_bus):
        super().__init__()
        self.setWindowTitle("Showcase: FolderGroupView")
        self.resize(960, 540)
        self.file_dialog = QFileDialog()
        tabs = QTabWidget()
        main_tab = MainTab(
            command_bus=command_bus,
            event_bus=event_bus,
        )
        settings_tab = SettingsTab()

        # add tabs in display order
        tabs.addTab(settings_tab, "⚙")
        tabs.addTab(main_tab, "Slideshow")

        # define focused tab (index starts at 0, default is first added)
        tabs.setCurrentIndex(1)
        self.setCentralWidget(tabs)

    def initialize(self): ...


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
            command_bus=command_bus,
            event_bus=event_bus,
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
