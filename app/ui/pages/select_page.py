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
        self.side_panel = QFrame()
        self.side_panel.setObjectName("selectSidePanel")
        self.side_title_label = QLabel("YOLO 环境工具")
        self.side_title_label.setObjectName("selectSideTitle")
        self.side_description_label = QLabel("专注安装可用环境，不强制下载模型权重。")
        self.side_description_label.setObjectName("selectSideDescription")
        self.side_description_label.setWordWrap(True)
        self.side_steps_label = QLabel(
            "1. 检测 Conda 与显卡\n"
            "2. 创建独立 YOLO 环境\n"
            "3. 安装 PyTorch 与 Ultralytics\n"
            "4. 支持取消长时间命令"
        )
        self.side_steps_label.setObjectName("selectSideSteps")
        self.side_steps_label.setWordWrap(True)
        self.side_tip_label = QLabel("推荐：非 C 盘安装")
        self.side_tip_label.setObjectName("selectSideTip")

        self.title_label = QLabel("YOLO 环境安装配置")
        self.title_label.setObjectName("selectTitleLabel")
        self.panel_title_label = QLabel("Conda 根目录与环境参数")
        self.panel_title_label.setObjectName("selectPanelTitle")
        self.summary_label = QLabel("选择环境名称、Python 版本和 Conda 根目录；模型权重默认不下载。")
        self.summary_label.setObjectName("selectSummaryLabel")
        self.summary_label.setWordWrap(True)
        self.install_dir_label = QLabel("Conda 根目录")
        self.install_dir_label.setObjectName("installDirLabel")
        self.env_name_edit = QLineEdit("yolo-env")
        self.env_name_edit.setObjectName("envNameEdit")
        self.python_version_combo = QComboBox()
        self.python_version_combo.setObjectName("pythonVersionCombo")
        self.python_version_combo.setEditable(True)
        self.python_version_combo.addItems(["3.10", "3.11", "3.12"])
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
        self.environment_hint_label = QLabel("Conda 根目录用于创建和删除环境，建议使用已检测到的 Anaconda/Miniconda 根目录。")
        self.environment_hint_label.setObjectName("environmentHintLabel")
        self.total_label = QLineEdit("模型权重：不下载")
        self.total_label.setObjectName("weightStatusLine")
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

        self.install_config_panel = QFrame()
        self.install_config_panel.setObjectName("installConfigPanel")
        config_panel_layout = QVBoxLayout(self.install_config_panel)
        config_panel_layout.setContentsMargins(18, 18, 18, 18)
        config_panel_layout.setSpacing(12)
        config_panel_layout.addWidget(self.panel_title_label)
        config_panel_layout.addWidget(self.summary_label)
        config_panel_layout.addWidget(self.environment_hint_label)
        config_panel_layout.addLayout(form)
        config_panel_layout.addStretch(1)
        config_panel_layout.addWidget(self.total_label)
        config_panel_layout.addWidget(self.start_button)

        side_layout = QVBoxLayout(self.side_panel)
        side_layout.setContentsMargins(24, 24, 24, 24)
        side_layout.setSpacing(18)
        side_layout.addWidget(self.side_title_label)
        side_layout.addWidget(self.side_description_label)
        side_layout.addSpacing(10)
        side_layout.addWidget(self.side_steps_label)
        side_layout.addStretch(1)
        side_layout.addWidget(self.side_tip_label)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)
        layout.addWidget(self.side_panel, 0)
        layout.addWidget(self.install_config_panel, 1)

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
        directory = QFileDialog.getExistingDirectory(self, "选择 Conda 根目录", self.workspace_edit.text().strip())
        if directory:
            self.workspace_edit.setText(directory)

    def validate_paths(self) -> bool:
        warning = install_path_warning(self.workspace_edit.text())
        self.path_warning_label.setText(warning or install_path_notice(self.workspace_edit.text()))
        self.start_button.setEnabled(not warning)
        return not warning
