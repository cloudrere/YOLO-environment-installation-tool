from __future__ import annotations

from PyQt6.QtWidgets import QPlainTextEdit


class LogView(QPlainTextEdit):
    def __init__(self, *, max_lines: int = 5000, max_line_length: int = 2000, parent=None):
        super().__init__(parent)
        self.max_lines = max_lines
        self.max_line_length = max_line_length
        self.setReadOnly(True)
        self.setObjectName("logView")

    def append_line(self, line: str) -> None:
        current = self.toPlainText().splitlines()
        current.append(line[: self.max_line_length])
        current = current[-self.max_lines :]
        self.setPlainText("\n".join(current))
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

