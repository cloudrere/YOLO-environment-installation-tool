from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QProgressBar, QPushButton, QVBoxLayout, QWidget

from app.core.pipeline import Pipeline
from app.ui import text
from app.ui.widgets.log_view import LogView


class InstallPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("installPage")
        self.step_labels: dict[str, QLabel] = {}
        self.title_label = QLabel("安装进度")
        self.title_label.setObjectName("pageTitleLabel")
        self.summary_label = QLabel("安装命令会按步骤执行，日志会实时显示在下方。")
        self.summary_label.setObjectName("pageSummaryLabel")
        self.summary_label.setWordWrap(True)
        self.log_view = LogView()
        self.log_view.setObjectName("installLogView")
        self.install_progress = QProgressBar()
        self.install_progress.setObjectName("installProgress")
        self.install_progress.setRange(0, 100)
        self.install_progress.setValue(0)
        self.conda_progress = QProgressBar()
        self.conda_progress.setObjectName("condaProgress")
        self.conda_progress.setRange(0, 0)
        self.conda_progress.hide()
        self.cancel_button = QPushButton(text.BUTTON_CANCEL)
        self.cancel_button.setObjectName("cancelInstallButton")
        self.uninstall_env_edit = QLineEdit("yolo-env")
        self.uninstall_env_edit.setObjectName("uninstallEnvEdit")
        self.uninstall_env_edit.setPlaceholderText("输入要删除的环境名")
        self.uninstall_button = QPushButton(text.BUTTON_UNINSTALL)
        self.uninstall_button.setObjectName("uninstallEnvButton")
        self.uninstall_button.setEnabled(True)
        self.uninstall_progress = QProgressBar()
        self.uninstall_progress.setObjectName("uninstallProgress")
        self.uninstall_progress.setRange(0, 0)
        self.uninstall_progress.hide()
        self.uninstall_env_edit.textChanged.connect(self._sync_uninstall_button)

        steps_panel = QFrame()
        steps_panel.setObjectName("installStepsPanel")
        steps_layout = QGridLayout(steps_panel)
        steps_layout.setContentsMargins(16, 14, 16, 14)
        steps_layout.setHorizontalSpacing(12)
        steps_layout.setVerticalSpacing(10)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        layout.addWidget(self.title_label)
        layout.addWidget(self.summary_label)
        for index, step in enumerate(Pipeline.STEPS):
            label = QLabel(f"{text.STEP_NAMES.get(step, step)}：{text.STEP_STATUS['pending']}")
            label.setObjectName(f"step_{step}")
            label.setProperty("stepStatus", "pending")
            self.step_labels[step] = label
            steps_layout.addWidget(label, index // 3, index % 3)

        log_panel = QFrame()
        log_panel.setObjectName("installLogPanel")
        log_layout = QVBoxLayout(log_panel)
        log_layout.setContentsMargins(16, 14, 16, 14)
        log_layout.setSpacing(10)
        self.log_title_label = QLabel("安装日志")
        self.log_title_label.setObjectName("sectionTitleLabel")
        log_layout.addWidget(self.log_title_label)
        log_layout.addWidget(self.install_progress)
        log_layout.addWidget(self.conda_progress)
        log_layout.addWidget(self.log_view, 1)

        actions = QHBoxLayout()
        actions.addWidget(self.cancel_button)
        actions.addStretch(1)

        uninstall_panel = QFrame()
        uninstall_panel.setObjectName("uninstallPanel")
        uninstall_layout = QHBoxLayout(uninstall_panel)
        uninstall_layout.setContentsMargins(16, 12, 16, 12)
        uninstall_layout.setSpacing(10)
        self.uninstall_title_label = QLabel("删除 Conda 环境")
        self.uninstall_title_label.setObjectName("sectionTitleLabel")
        uninstall_layout.addWidget(self.uninstall_title_label)
        uninstall_layout.addWidget(self.uninstall_env_edit, 1)
        uninstall_layout.addWidget(self.uninstall_button)
        uninstall_layout.addWidget(self.uninstall_progress)

        layout.addWidget(steps_panel)
        layout.addWidget(log_panel, 1)
        layout.addLayout(actions)
        layout.addWidget(uninstall_panel)

    def set_step(self, step: str, status: str) -> None:
        if step in self.step_labels:
            self.step_labels[step].setText(f"{text.STEP_NAMES.get(step, step)}：{text.STEP_STATUS.get(status, status)}")
            self.step_labels[step].setProperty("stepStatus", status)
            self.step_labels[step].style().unpolish(self.step_labels[step])
            self.step_labels[step].style().polish(self.step_labels[step])
            self._sync_install_progress()

    def append_log(self, line: str) -> None:
        self.log_view.append_line(line)

    def set_finished(self, ok: bool, message: str) -> None:
        if message:
            self.append_log(message)
        if ok:
            self.install_progress.setValue(100)
        self._sync_uninstall_button()

    def _sync_uninstall_button(self) -> None:
        self.uninstall_button.setEnabled(bool(self.uninstall_env_edit.text().strip()))

    def set_miniconda_installing(self, running: bool) -> None:
        self.conda_progress.setVisible(running)

    def set_uninstall_running(self, running: bool) -> None:
        self.uninstall_progress.setVisible(running)
        self.uninstall_button.setEnabled(not running and bool(self.uninstall_env_edit.text().strip()))

    def _sync_install_progress(self) -> None:
        total = len(Pipeline.STEPS)
        completed = sum(1 for label in self.step_labels.values() if label.property("stepStatus") == "ok")
        running = any(label.property("stepStatus") == "running" for label in self.step_labels.values())
        value = int((completed / total) * 100)
        if running:
            value = max(value, int(((completed + 0.35) / total) * 100))
        self.install_progress.setValue(min(value, 100))
