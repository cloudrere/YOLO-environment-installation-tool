from __future__ import annotations

import json
from pathlib import Path

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.ui.widgets.model_card import ModelCard
from app.core.validation import install_path_warning
from app.ui import text
from app.utils.paths import resource_path


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
        self.python_version_combo = QComboBox()
        self.python_version_combo.setObjectName("pythonVersionCombo")
        self.python_version_combo.setEditable(True)
        self.python_version_combo.addItems(["3.10", "3.11"])
        self.workspace_edit = QLineEdit(str(Path.home() / "yolo_workspace"))
        self.workspace_edit.setObjectName("workspaceEdit")
        self.browse_workspace_button = QPushButton("浏览...")
        self.browse_workspace_button.setObjectName("browseWorkspaceButton")
        self.path_warning_label = QLineEdit("")
        self.path_warning_label.setObjectName("pathWarningLabel")
        self.path_warning_label.setReadOnly(True)
        self.jupyter_check = QCheckBox(text.LABEL_INSTALL_JUPYTER)
        self.shortcut_check = QCheckBox(text.LABEL_CREATE_SHORTCUT)
        self.start_button = QPushButton(text.BUTTON_START)
        self.start_button.setObjectName("startInstallButton")
        self.weights_hint_label = QLabel("模型权重为可选项；只安装 YOLO 环境时可以不选择。")
        self.weights_hint_label.setObjectName("weightsHintLabel")
        self.total_label = QLineEdit(self._weights_count_text())
        self.total_label.setReadOnly(True)

        self._load_models(data_path)

        form = QFormLayout()
        workspace_row = QHBoxLayout()
        workspace_row.addWidget(self.workspace_edit, 1)
        workspace_row.addWidget(self.browse_workspace_button)
        form.addRow(text.LABEL_ENVIRONMENT, self.env_name_edit)
        form.addRow("Python 版本", self.python_version_combo)
        form.addRow(text.LABEL_WORKSPACE, workspace_row)
        form.addRow(text.LABEL_WARNING, self.path_warning_label)
        form.addRow("", self.jupyter_check)
        form.addRow("", self.shortcut_check)

        footer = QHBoxLayout()
        footer.addWidget(self.total_label, 1)
        footer.addWidget(self.start_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self.weights_hint_label)
        layout.addWidget(self.tabs, 1)
        layout.addLayout(form)
        layout.addLayout(footer)

        self.start_button.clicked.connect(lambda: self.install_requested.emit(self.build_config()))
        self.workspace_edit.textChanged.connect(lambda: self.validate_paths())
        self.browse_workspace_button.clicked.connect(self.choose_workspace_directory)

    def _load_models(self, data_path: str) -> None:
        path = Path(data_path)
        if not path.is_absolute():
            path = resource_path(data_path)
        data = json.loads(path.read_text(encoding="utf-8"))
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
        self.total_label.setText(self._weights_count_text())

    def _weights_count_text(self) -> str:
        return f"可选下载权重：{len(self.selected_weights())} 个"

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
            "python_version": self.python_version_combo.currentText().strip() or "3.10",
            "workspace": self.workspace_edit.text().strip(),
            "weights": self.selected_weights(),
            "install_jupyter": self.jupyter_check.isChecked(),
            "make_shortcut": self.shortcut_check.isChecked(),
            "pip_mirror": "https://pypi.tuna.tsinghua.edu.cn/simple",
        }

    def choose_workspace_directory(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "选择安装目录", self.workspace_edit.text().strip())
        if directory:
            self.workspace_edit.setText(directory)

    def validate_paths(self) -> bool:
        warning = install_path_warning(self.workspace_edit.text())
        self.path_warning_label.setText(warning)
        self.start_button.setEnabled(not warning)
        return not warning
