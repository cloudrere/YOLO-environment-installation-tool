from __future__ import annotations

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
    QVBoxLayout,
    QWidget,
)

from app.core.validation import install_path_notice, install_path_warning
from app.ui import text


class SelectPage(QWidget):
    install_requested = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("selectPage")
        self.model_cards: list = []
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
        self.environment_hint_label = QLabel("此工具只安装 YOLO 运行环境，不默认下载模型权重。")
        self.environment_hint_label.setObjectName("environmentHintLabel")
        self.total_label = QLineEdit("模型权重：不下载")
        self.total_label.setReadOnly(True)

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
        layout.addWidget(self.environment_hint_label)
        layout.addLayout(form)
        layout.addLayout(footer)

        self.start_button.clicked.connect(lambda: self.install_requested.emit(self.build_config()))
        self.workspace_edit.textChanged.connect(lambda: self.validate_paths())
        self.browse_workspace_button.clicked.connect(self.choose_workspace_directory)

    def selected_weights(self) -> list[str]:
        return []

    def select_weight(self, weight: str) -> None:
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
        self.path_warning_label.setText(warning or install_path_notice(self.workspace_edit.text()))
        self.start_button.setEnabled(not warning)
        return not warning
