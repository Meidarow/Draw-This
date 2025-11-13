from PySide6.QtCore import QSize, QPoint
from PySide6.QtGui import QAction, Qt
from PySide6.QtWidgets import (
    QTreeView,
    QVBoxLayout,
    QMenu,
    QFrame,
    QStackedWidget,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QAbstractScrollArea,
)

from iteradraw.application.commands.folder_commands import AddFolderSetCommand
from iteradraw.domain.events.domain_events import (
    FolderSetAdded,
    FolderSetRemoved,
)
from iteradraw.domain.models.folder import FolderSet
from iteradraw.presentation.pyside.viewmodels.folder_group_viewmodel import (
    FolderGroupViewModel,
)

"""
Custom PySide QtGui views for the folder panel of the main tab.
"""


class FolderPanelView(QStackedWidget):
    """
        Aggregate view of FolderGroupViews.
    QStackedWidget
    """

    class _UiBuilder:
        def __init__(self, parent: QStackedWidget):
            self._parent = parent

        def build(self) -> None:
            self._configure_widget()
            self._build_placeholder()  # Inserts placeholder at index 0
            self._build_content()  # Inserts content at index 1

        def _configure_widget(self) -> None:
            self._parent.setObjectName("FolderGroupBox")
            self._parent.setContextMenuPolicy(
                Qt.ContextMenuPolicy.CustomContextMenu
            )

        def _build_placeholder(self) -> None:
            """
            Build the header for the folder section of the GUI.
            Includes a button to add more FolderSets and section title.
            """
            self.placeholder = QLabel()
            self.placeholder.setText("Right-click to add folders!")
            self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.placeholder.setContextMenuPolicy(
                Qt.ContextMenuPolicy.NoContextMenu
            )
            self._parent.addWidget(self.placeholder)

        def _build_content(self) -> None:
            self.layout = QVBoxLayout()
            self.content = QFrame()
            self.content.setLayout(self.layout)
            self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            self.scroll_area = QScrollArea()
            self.scroll_area.setWidget(self.content)
            self.scroll_area.setWidgetResizable(True)

            self._parent.addWidget(self.scroll_area)

    def __init__(self, command_bus, event_bus):
        super().__init__()
        self.command_bus = command_bus
        self.event_bus = event_bus
        self._ui = self._UiBuilder(self)
        self._ui.build()
        self.content = self._ui.content.layout()
        self._bind_signals()

    def _bind_signals(self) -> None:
        self.customContextMenuRequested.connect(self.on_context_menu_requested)
        self.event_bus.subscribe(
            FolderSetAdded,
            lambda event: self.on_folderset_added(event.folderset),
        )
        self.event_bus.subscribe(
            FolderSetRemoved,
            self.on_folderset_removed,
        )

    # =============================================================================
    # Signal Slots
    #    Slots for signals emmited in the GUI
    #
    # Naming convention:
    #    on_"command"() -> command describes GUI action
    # =============================================================================

    def on_add_folder_group(self) -> None:
        auto_name = self._determine_folder_group_name()
        self.add_folderset(folderset_name=auto_name)

    # =============================================================================
    # Command Dispatchers:
    #    Methods that issue commands on the command bus.
    #
    # Naming convention:
    #    "action"() -> action describes application layer command
    # =============================================================================

    def add_folderset(self, folderset_name: str):
        cmd = AddFolderSetCommand(display_name=folderset_name)
        self.command_bus.dispatch(cmd)

    # =============================================================================
    # Event Slots:
    #    Slots for events isued on the event_bus
    #
    # Naming convention:
    #    on_"event_happened"() -> event describes past happening
    # =============================================================================

    def on_folderset_removed(self, event: FolderSetRemoved) -> None:
        for index in range(self.content.count()):
            widget = self.content.itemAt(index).widget()
            if not isinstance(widget, FolderGroupView):
                continue
            root_item = widget.model.invisibleRootItem().child(0)
            widget_id = root_item.data(Qt.ItemDataRole.UserRole)
            if not widget_id == event.folderset_id:
                continue
            self.content.removeWidget(widget)
            widget.deleteLater()
            break
        self._set_current_top_panel()

    def on_folderset_added(self, folderset: FolderSet) -> None:
        folder_group = FolderGroupView()
        vm = FolderGroupViewModel(
            self.command_bus, self.event_bus, folder_group
        )
        folder_group.assign_viewmodel_and_build(vm)
        vm.populate(folderset)
        self.content.addWidget(folder_group)
        self._set_current_top_panel()

    def on_context_menu_requested(self, position) -> None:
        """
        Builds and shows the correct context menu on the fly.
        """
        menu = QMenu()  # Create a new, fresh menu

        # Case 1: Clicked on group or empty space
        self._add_action(menu, "Add folder group", self.on_add_folder_group)

        menu.exec(self.mapToGlobal(position))

    # =============================================================================
    # Private Helpers:
    # =============================================================================
    @staticmethod
    def _add_action(menu: QMenu, text: str, slot) -> None:
        """
        Private helper factory to create, connect, and add an action.
        """
        action = QAction(text, menu)
        action.triggered.connect(slot)
        menu.addAction(action)

    @staticmethod
    def _determine_folder_group_name() -> str:
        """
        Method returns the placeholder name for new folder groups.
        """
        return "New Folder Group"

    def _set_current_top_panel(self):
        if self.content.isEmpty():
            self.setCurrentIndex(0)
        else:
            self.setCurrentIndex(1)


class FolderGroupView(QTreeView):
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

        def build(self):
            self._configure_tree()

        def _configure_tree(self):
            self._parent.setModel(self._parent.model)
            self._parent.setObjectName("FolderGroupItem")
            self._parent.setContextMenuPolicy(
                Qt.ContextMenuPolicy.CustomContextMenu
            )
            self._parent.setHeaderHidden(True)
            # Enable Drag/Drop behavior
            self._parent.setAcceptDrops(True)
            self._parent.setDragEnabled(True)
            self._parent.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            policy = self._parent.sizePolicy()
            policy.setVerticalPolicy(QSizePolicy.Policy.Minimum)
            self._parent.setSizePolicy(policy)
            self._parent.setSizeAdjustPolicy(
                QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents
            )

    def __init__(self):
        super().__init__()
        self.model = None
        self._ui = self._UiBuilder(self)

    # noinspection PyUnresolvedReferences
    def assign_viewmodel_and_build(self, viewmodel: FolderGroupViewModel):
        self.model = viewmodel
        self._ui.build()
        self.customContextMenuRequested.connect(self.on_context_menu_requested)
        self.expanded.connect(self._on_tree_changed)
        self.collapsed.connect(self._on_tree_changed)

    def on_context_menu_requested(self, position):
        """
        Builds and shows the correct context menu on the fly.
        """
        index = self.indexAt(position)
        menu = QMenu()  # Create a new, fresh menu

        # Case 1: Clicked on group or empty space
        if (
            not index.isValid()
            or self.model.itemFromIndex(index).hasChildren()
        ):
            self._add_action(
                menu,
                "Add folder",
                lambda: self.model.on_add_folder_to_group(),
            )
            self._add_action(
                menu,
                "Delete group",
                lambda: self.model.on_delete_folder_group(),
            )
            self._add_action(
                menu,
                "Rename group",
                lambda: self.model.on_rename_folder_group(),
            )

        # Case 2: Clicked on a child folder
        else:
            item = self.model.itemFromIndex(index)
            self._add_action(
                menu,
                "Remove folder",
                lambda: self.model.on_remove_folder_from_group(item),
            )
            self._add_action(
                menu,
                "Open folder",
                lambda: self.model.on_open_folder_from_group(item),
            )

        menu.exec(self.viewport().mapToGlobal(position))

    @staticmethod
    def _add_action(menu: QMenu, text: str, slot):
        """
        Private helper factory to create, connect, and add an action.
        """
        action = QAction(text, menu)
        action.triggered.connect(slot)
        menu.addAction(action)

    def _on_tree_changed(self):
        """Called when tree expands/collapses - trigger resize"""
        self.updateGeometry()  # Tells parent layout to recalculate

    def on_expansion_changed(self, index):
        """
        Forces the parent layout to re-calculate our size.
        """
        self.updateGeometry()

    def minimumSizeHint(self) -> QSize:
        """
        Our minimum size is *just* the root item.
        This kills the "weird box".
        """
        if not self.model:
            return super().minimumSizeHint()

        # Get height of the root item (row 0)
        root_index = self.model().index(0, 0)
        height = self.rowHeight(root_index)

        # Add 2px for any borders/padding
        return QSize(super().minimumSizeHint().width(), height + 2)

    def sizeHint(self) -> QSize:
        """
        Our "ideal" size is the height of *all* visible items.
        This is the "banger" version of Claude's "iffy" logic.
        """
        if not self.model:
            return super().sizeHint()

        height = 0

        # This is the "god-tier" way to get *only* visible rows
        index = self.indexAt(QPoint(0, 0))  # Start at top-left
        while index.isValid():
            height += self.rowHeight(index)
            index = self.indexBelow(index)  # Get next *visible* item

        # Add 2px for any borders/padding
        return QSize(super().sizeHint().width(), height + 2)
