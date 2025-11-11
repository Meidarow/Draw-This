"""
Viewmodels for interface between GUI layer and application layer.
"""

from PySide6.QtGui import QStandardItemModel, QStandardItem, Qt

from iteradraw.application.commands.folder_commands import (
    AddFolderCommand,
    RemoveFolderCommand,
    SetAllFoldersEnabledCommand,
    SetFolderEnabledCommand,
)


class FolderGroupViewModel(QStandardItemModel):
    def __init__(self, command_bus, event_bus):
        super().__init__()
        self.command_bus = command_bus
        self.event_bus = event_bus
        self.is_handling_change = False
        self.assign_signals()

    def assign_signals(self):
        self.itemChanged.connect(self.on_checkbox_changed)

    def populate(self, folderset):
        self.itemChanged.disconnect(self.on_checkbox_changed)
        group = QStandardItem(folderset.display_name)
        group.setDropEnabled(True)
        group.setDragEnabled(False)
        group.setCheckable(True)
        group.setAutoTristate(True)
        group.setData(
            folderset.uuid,
            Qt.ItemDataRole.UserRole,
        )
        self.invisibleRootItem().appendRow(group)

        for f in folderset.all:
            item = QStandardItem(f.path)
            item.setDragEnabled(True)
            item.setDropEnabled(False)
            item.setCheckable(True)
            item.setCheckState(
                Qt.CheckState.Checked if f.enabled else Qt.CheckState.Unchecked
            )
            group.appendRow(item)
        self.itemChanged.connect(self.on_checkbox_changed)

    def add_folder(self):
        cmd = AddFolderCommand(
            folder_path="",
            enabled=True,
            folderset_id="",
        )
        self.command_bus.dispatch(cmd)

    def remove_folder(self):
        cmd = RemoveFolderCommand(folder_path="", folderset_id="")
        self.command_bus.dispatch(cmd)

    def on_checkbox_changed(self, item: QStandardItem):
        if self.is_handling_change:
            return
        self.is_handling_change = True
        if item.hasChildren():
            new_state = item.checkState()
            for child_row in range(item.rowCount()):
                child = item.child(child_row)
                child.setCheckState(new_state)

            cmd = SetAllFoldersEnabledCommand(
                folderset_id=item.data(Qt.ItemDataRole.UserRole),
                target_enabled=(Qt.CheckState.Checked == new_state),
            )
            self.command_bus.dispatch(cmd)
        else:
            parent = item.parent()
            checked_count = 0
            total_children = parent.rowCount()

            for i in range(total_children):
                if parent.child(i).checkState() == Qt.CheckState.Checked:
                    checked_count += 1

            if checked_count == 0:
                parent.setCheckState(Qt.CheckState.Unchecked)
            elif checked_count == total_children:
                parent.setCheckState(Qt.CheckState.Checked)
            else:
                parent.setCheckState(Qt.CheckState.PartiallyChecked)

            cmd = SetFolderEnabledCommand(
                folderset_id=parent.data(Qt.ItemDataRole.UserRole),
                folder_path=item.text(),
                target_enabled=(Qt.CheckState.Checked == item.checkState()),
            )
            self.command_bus.dispatch(cmd)
        self.is_handling_change = False
