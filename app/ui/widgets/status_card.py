from __future__ import annotations

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class StatusCard(QWidget):
    def __init__(self, title: str, value: str = "", detail: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("statusCard")
        self.title_label = QLabel(title)
        self.title_label.setObjectName("statusCardTitle")
        self.value_label = QLabel(value)
        self.value_label.setObjectName("statusCardValue")
        self.detail_label = QLabel(detail)
        self.detail_label.setObjectName("statusCardDetail")
        self.detail_label.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.detail_label)

    def set_status(self, value: str, detail: str = "") -> None:
        self.value_label.setText(value)
        self.detail_label.setText(detail)

