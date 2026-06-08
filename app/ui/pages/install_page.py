from __future__ import annotations

from PyQt6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from app.core.pipeline import Pipeline
from app.ui import text
from app.ui.widgets.log_view import LogView


class InstallPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("installPage")
        self.step_labels: dict[str, QLabel] = {}
        self.log_view = LogView()
        self.cancel_button = QPushButton(text.BUTTON_CANCEL)
        self.try_button = QPushButton(text.BUTTON_TRY)
        self.try_button.setEnabled(False)
        self.uninstall_button = QPushButton(text.BUTTON_UNINSTALL)
        self.uninstall_button.setEnabled(False)

        layout = QVBoxLayout(self)
        for step in Pipeline.STEPS:
            label = QLabel(f"{text.STEP_NAMES.get(step, step)}：{text.STEP_STATUS['pending']}")
            label.setObjectName(f"step_{step}")
            self.step_labels[step] = label
            layout.addWidget(label)
        layout.addWidget(self.log_view, 1)
        layout.addWidget(self.cancel_button)
        layout.addWidget(self.try_button)
        layout.addWidget(self.uninstall_button)

    def set_step(self, step: str, status: str) -> None:
        if step in self.step_labels:
            self.step_labels[step].setText(f"{text.STEP_NAMES.get(step, step)}：{text.STEP_STATUS.get(status, status)}")

    def append_log(self, line: str) -> None:
        self.log_view.append_line(line)

    def set_finished(self, ok: bool, message: str) -> None:
        if message:
            self.append_log(message)
        self.try_button.setEnabled(ok)
        self.uninstall_button.setEnabled(ok)
