from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
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
        self.title_label = QLabel("YOLO 环境安装配置")
        self.title_label.setObjectName("selectTitleLabel")
        self.summary_label = QLabel("选择环境名称、Python 版本和安装目录；模型权重默认不下载。")
        self.summary_label.setObjectName("selectSummaryLabel")
        self.summary_label.setWordWrap(True)
        self.install_dir_label = QLabel("安装目录")
        self.install_dir_label.setObjectName("installDirLabel")
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
        self.path_warning_label = QLabel("")
        self.path_warning_label.setObjectName("pathWarningLabel")
        self.path_warning_label.setWordWrap(True)
        self.jupyter_check = QCheckBox(text.LABEL_INSTALL_JUPYTER)
        self.shortcut_check = QCheckBox(text.LABEL_CREATE_SHORTCUT)
        self.start_button = QPushButton(text.BUTTON_START)
        self.start_button.setObjectName("startInstallButton")
        self.environment_hint_label = QLabel("安装目录建议放在 D/E 等非系统盘，路径尽量使用英文和数字。")
        self.environment_hint_label.setObjectName("environmentHintLabel")
        self.total_label = QLineEdit("模型权重：不下载")
        self.total_label.setReadOnly(True)

        form = QFormLayout()
        workspace_row = QHBoxLayout()
        workspace_row.addWidget(self.workspace_edit, 1)
        workspace_row.addWidget(self.browse_workspace_button)
        form.addRow(text.LABEL_ENVIRONMENT, self.env_name_edit)
        form.addRow("Python 版本", self.python_version_combo)
        form.addRow(self.install_dir_label, workspace_row)
        form.addRow(text.LABEL_WARNING, self.path_warning_label)
        form.addRow("", self.jupyter_check)
        form.addRow("", self.shortcut_check)

        config_panel = QFrame()
        config_panel.setObjectName("installConfigPanel")
        config_panel_layout = QVBoxLayout(config_panel)
        config_panel_layout.setContentsMargins(18, 18, 18, 18)
        config_panel_layout.setSpacing(12)
        config_panel_layout.addLayout(form)

        footer = QHBoxLayout()
        footer.addWidget(self.total_label, 1)
        footer.addWidget(self.start_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)
        layout.addWidget(self.title_label)
        layout.addWidget(self.summary_label)
        layout.addWidget(self.environment_hint_label)
        layout.addWidget(config_panel)
        layout.addLayout(footer)

        self.start_button.clicked.connect(lambda: self.install_requested.emit(self.build_config()))
        self.workspace_edit.textChanged.connect(lambda: self.validate_paths())
        self.browse_workspace_button.clicked.connect(self.choose_workspace_directory)
        self.validate_paths()

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
