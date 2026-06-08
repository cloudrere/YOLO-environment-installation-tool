from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QCheckBox, QComboBox, QHBoxLayout, QLabel, QWidget

from app.ui import text


class ModelCard(QWidget):
    selection_changed = pyqtSignal()

    def __init__(self, model_id: str, label: str, scales: list[str], suffix: str = "", parent=None):
        super().__init__(parent)
        self.model_id = model_id
        self.suffix = suffix
        self.checkbox = QCheckBox(label)
        self.checkbox.setObjectName(f"modelCheck_{model_id}_{suffix}".replace("-", "_"))
        self.scale_combo = QComboBox()
        self.scale_combo.setObjectName(f"modelScale_{model_id}_{suffix}".replace("-", "_"))
        self.scale_combo.addItems(scales or [""])
        self.size_label = QLabel("可选权重")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.addWidget(self.checkbox, 1)
        layout.addWidget(QLabel(text.LABEL_SCALE))
        layout.addWidget(self.scale_combo)
        layout.addWidget(self.size_label)

        self.checkbox.toggled.connect(self.selection_changed.emit)
        self.scale_combo.currentTextChanged.connect(self.selection_changed.emit)

    def selected_weight(self) -> str | None:
        if not self.checkbox.isChecked():
            return None
        scale = self.scale_combo.currentText()
        if scale in {"-tiny", "-spp"}:
            return f"{self.model_id}{scale}.pt"
        return f"{self.model_id}{scale}{self.suffix}.pt"
