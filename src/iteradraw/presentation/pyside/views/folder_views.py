from typing import Optional

from PySide6.QtGui import QAction, Qt
from PySide6.QtWidgets import (
    QWidget,
    QTreeView,
    QVBoxLayout,
    QMenu,
    QFrame,
    QGroupBox,
)

from iteradraw.application.commands.folder_commands import AddFolderSetCommand
from iteradraw.domain.events.domain_events import FolderSetAdded
from iteradraw.domain.models.folder import FolderSet
from iteradraw.presentation.pyside.viewmodels.folder_group_viewmodel import (
    FolderGroupViewModel,
)

"""
Custom PySide QtGui views for the folder panel of the main tab.
"""


class FolderPanelView(QGroupBox):
    """
        Aggregate view of FolderGroupViews.
    QStackedWidget
    """

    class _UiBuilder:
        def __init__(self, parent):
            self._parent = parent

        def build(self):
            self._configure_widget()
            self._build_placeholder()
            self._build_content()
            self._install_layout()

        def _configure_widget(self):
            self._parent.setObjectName("FolderGroupBox")

        def _build_placeholder(self):
            """
            Build the header for the folder section of the GUI.

            Includes a button to add more FolderSets and section title.
            """
            self.placeholder = QFrame()

        def _build_content(self):
            """"""

        def _install_layout(self):
            self.layout = QVBoxLayout()
            self._parent.setLayout(self.layout)

    def __init__(self, command_bus, event_bus):
        super().__init__()
        self.command_bus = command_bus
        self.event_bus = event_bus
        self._ui = self._UiBuilder(self)
        self._ui.build()
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._bind_signals()

    def _bind_signals(self):
        self.customContextMenuRequested.connect(self.on_context_menu_requested)

        self.event_bus.subscribe(
            FolderSetAdded,
            lambda event: self.add_folder_group(event.folderset),
        )

    def on_add_folder_group(self):
        auto_name = self._determine_folder_group_name()
        self.add_folderset(folderset_name=auto_name)

    def add_folderset(self, folderset_name: Optional[str]):
        cmd = AddFolderSetCommand(display_name=folderset_name)
        self.command_bus.dispatch(cmd)

    def on_folderset_added(self, folderset: FolderSet):
        folder_group = FolderGroupView()
        vm = FolderGroupViewModel(
            self.command_bus, self.event_bus, folder_group
        )
        folder_group.assign_viewmodel_and_build(vm)
        vm.populate(folderset)
        self.layout().addWidget(folder_group)

    def remove_folder_group(self):
        ...

    def _determine_folder_group_name(self) -> str:
        """
        Method returns the placeholder name for new folder groups.
        """
        return "New Folder Group"

    def on_context_menu_requested(self, position):
        """
        Builds and shows the correct context menu on the fly.
        """
        menu = QMenu()  # Create a new, fresh menu

        # Case 1: Clicked on group or empty space
        self._add_action(menu, "Add folder group", self.on_add_folder_group)

        menu.exec(self.mapToGlobal(position))

    def _add_action(self, menu: QMenu, text: str, slot):
        """
        Private helper factory to create, connect, and add an action.
        """
        action = QAction(text, menu)
        action.triggered.connect(slot)
        menu.addAction(action)


class FolderGroupView(QWidget):
    """
    Widget for single FolderSet's folder group.
    A tree with checkboxes, triple state for the tree-root and double state
    for each branch.

    Core Behaviors:
        -Accepts drop operations on unique folders, and rejects duplicates.
        -Defines context menu actions for the folder group and its folders.
        Actions:
            ADD_FOLDER
            REMOVE_FOLDER
            OPEN_FOLDER
            DELETE_FOLDERSET
            RENAME_FOLDERSET

    Note: Data-bound, uses View <-> Viewmodel architecture.
          Its viewmodel class is FolderGroupViewModel.
    """

    class _UiBuilder:
        """
        Handles all reusable UI building implementation.

        Core Responsabilites:
            -Create/Configure tree view UI parameters.
            -Install the tree view into parent.
        """

        def __init__(self, parent):
            self._parent = parent
            self.tree: Optional[QTreeView] = None

        def build(self):
            self._create_widget()
            self._configure_tree()
            self._install_layout()

        def _create_widget(self):
            self.tree = QTreeView()

        def _configure_tree(self):
            self.tree.setModel(self._parent.model)
            self.tree.setObjectName("FolderGroupItem")
            self.tree.setContextMenuPolicy(
                Qt.ContextMenuPolicy.CustomContextMenu
            )
            self.tree.setHeaderHidden(True)
            # Enable Drag/Drop behavior
            self.tree.setAcceptDrops(True)
            self.tree.setDragEnabled(True)

        def _install_layout(self):
            main_layout = QVBoxLayout(self._parent)
            main_layout.addWidget(self.tree)

    def __init__(self):
        super().__init__()
        self.model = None
        self.tree = None
        self._ui = self._UiBuilder(self)

    def assign_viewmodel_and_build(self, viewmodel: FolderGroupViewModel):
        self.model = viewmodel
        self._ui.build()
        self.tree = self._ui.tree
        self.tree.customContextMenuRequested.connect(
            self.on_context_menu_requested
        )

    def on_context_menu_requested(self, position):
        """
        Builds and shows the correct context menu on the fly.
        """
        index = self.tree.indexAt(position)
        menu = QMenu()  # Create a new, fresh menu

        # Case 1: Clicked on group or empty space
        if (
            not index.isValid()
            or self.model.itemFromIndex(index).hasChildren()
        ):
            self._add_action(
                menu,
                "Add folder",
                lambda: self.model.on_add_folder_to_group(position),
            )
            self._add_action(
                menu,
                "Delete group",
                lambda: self.model.on_delete_folder_group(position),
            )
            self._add_action(
                menu,
                "Rename group",
                lambda: self.model.on_rename_folder_group(position),
            )

        # Case 2: Clicked on a child folder
        else:
            item = self.model.itemFromIndex(index)
            self._add_action(
                menu,
                "Remove folder",
                lambda: self.model.on_remove_folder_from_group(item, position),
            )
            self._add_action(
                menu,
                "Open folder",
                lambda: self.model.on_open_folder_from_group(item, position),
            )

        menu.exec(self.tree.viewport().mapToGlobal(position))

    def _add_action(self, menu: QMenu, text: str, slot):
        """
        Private helper factory to create, connect, and add an action.
        """
        action = QAction(text, menu)
        action.triggered.connect(slot)
        menu.addAction(action)
