from __future__ import annotations

import json
from pathlib import Path

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.ui.widgets.model_card import ModelCard
from app.core.validation import install_path_warning


class SelectPage(QWidget):
    install_requested = pyqtSignal(dict)

    def __init__(self, data_path: str = "app/data/yolo_models.json", parent=None):
        super().__init__(parent)
        self.setObjectName("selectPage")
        self.model_cards: list[ModelCard] = []
        self.tabs = QTabWidget()
        self.tabs.setObjectName("modelTabs")
        self.env_name_edit = QLineEdit("yolo-env")
        self.env_name_edit.setObjectName("envNameEdit")
        self.workspace_edit = QLineEdit(str(Path.home() / "yolo_workspace"))
        self.workspace_edit.setObjectName("workspaceEdit")
        self.path_warning_label = QLineEdit("")
        self.path_warning_label.setObjectName("pathWarningLabel")
        self.path_warning_label.setReadOnly(True)
        self.jupyter_check = QCheckBox("Install Jupyter")
        self.shortcut_check = QCheckBox("Create desktop shortcut")
        self.start_button = QPushButton("Start")
        self.start_button.setObjectName("startInstallButton")
        self.total_label = QLineEdit("0 selected")
        self.total_label.setReadOnly(True)

        self._load_models(data_path)

        form = QFormLayout()
        form.addRow("Environment", self.env_name_edit)
        form.addRow("Workspace", self.workspace_edit)
        form.addRow("Warning", self.path_warning_label)
        form.addRow("", self.jupyter_check)
        form.addRow("", self.shortcut_check)

        footer = QHBoxLayout()
        footer.addWidget(self.total_label, 1)
        footer.addWidget(self.start_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs, 1)
        layout.addLayout(form)
        layout.addLayout(footer)

        self.start_button.clicked.connect(lambda: self.install_requested.emit(self.build_config()))
        self.workspace_edit.textChanged.connect(lambda: self.validate_paths())

    def _load_models(self, data_path: str) -> None:
        data = json.loads(Path(data_path).read_text(encoding="utf-8"))
        for group in data["groups"]:
            container = QWidget()
            group_layout = QVBoxLayout(container)
            for item in group["items"]:
                if "weights" in item:
                    for weight in item["weights"]:
                        card = ModelCard(item["id"], weight, [""], "")
                        card.selected_weight = lambda weight=weight, card=card: weight if card.checkbox.isChecked() else None
                        self._add_card(group_layout, card)
                else:
                    card = ModelCard(item["id"], item["label"], item.get("scales", [""]), item.get("suffix", ""))
                    self._add_card(group_layout, card)
            group_layout.addStretch(1)
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(container)
            self.tabs.addTab(scroll, group["key"])

    def _add_card(self, layout: QVBoxLayout, card: ModelCard) -> None:
        card.selection_changed.connect(self._update_total)
        self.model_cards.append(card)
        layout.addWidget(card)

    def _update_total(self) -> None:
        self.total_label.setText(f"{len(self.selected_weights())} selected")

    def selected_weights(self) -> list[str]:
        return [weight for card in self.model_cards if (weight := card.selected_weight())]

    def select_weight(self, weight: str) -> None:
        for card in self.model_cards:
            for i in range(card.scale_combo.count()):
                card.scale_combo.setCurrentIndex(i)
                if card.selected_weight() == weight or f"{card.model_id}{card.scale_combo.currentText()}{card.suffix}.pt" == weight:
                    card.checkbox.setChecked(True)
                    self._update_total()
                    return

    def build_config(self) -> dict:
        return {
            "env_name": self.env_name_edit.text().strip() or "yolo-env",
            "python_version": "3.10",
            "workspace": self.workspace_edit.text().strip(),
            "weights": self.selected_weights(),
            "install_jupyter": self.jupyter_check.isChecked(),
            "make_shortcut": self.shortcut_check.isChecked(),
            "pip_mirror": "https://pypi.tuna.tsinghua.edu.cn/simple",
        }

    def validate_paths(self) -> bool:
        warning = install_path_warning(self.workspace_edit.text())
        self.path_warning_label.setText(warning)
        self.start_button.setEnabled(not warning)
        return not warning
