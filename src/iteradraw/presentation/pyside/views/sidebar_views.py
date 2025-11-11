from PySide6.QtWidgets import (
    QWidget,
    QGroupBox,
    QFormLayout,
    QCheckBox,
    QSpinBox,
    QPushButton,
)


class SidePanelView(QGroupBox):
    def __init__(self):
        super().__init__()
        form = QFormLayout()
        form.addRow("Timer (seconds):", QSpinBox())
        form.addRow("Shuffle:", QCheckBox())
        form.addRow(QPushButton("Start"))
        self.setLayout(form)


class TimerSelectionView(QWidget):
    ...


class TriggerConsoleView(QWidget):
    ...
