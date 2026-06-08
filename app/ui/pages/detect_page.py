from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from app.core.detector import EnvSnapshot
from app.ui import text
from app.ui.widgets.status_card import StatusCard


class DetectPage(QWidget):
    next_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("detectPage")
        self.title_label = QLabel("环境检测")
        self.title_label.setObjectName("pageTitleLabel")
        self.summary_label = QLabel("先检测系统、Conda、显卡和磁盘信息，再进入安装配置。")
        self.summary_label.setObjectName("pageSummaryLabel")
        self.summary_label.setWordWrap(True)
        self.os_card = StatusCard(text.LABEL_OS, text.STATUS_NOT_CHECKED)
        self.conda_card = StatusCard(text.LABEL_CONDA, text.STATUS_NOT_CHECKED)
        self.gpu_card = StatusCard(text.LABEL_GPU, text.STATUS_NOT_CHECKED)
        self.disk_card = StatusCard(text.LABEL_DISK, text.STATUS_NOT_CHECKED)
        self.conda_envs_title_label = QLabel("当前 Conda 环境")
        self.conda_envs_title_label.setObjectName("sectionTitleLabel")
        self.conda_envs_label = QLabel("未检测")
        self.conda_envs_label.setObjectName("condaEnvsLabel")
        self.conda_envs_label.setWordWrap(True)
        self.detect_button = QPushButton(text.BUTTON_DETECT)
        self.detect_button.setObjectName("detectButton")
        self.next_button = QPushButton(text.BUTTON_NEXT)
        self.next_button.setObjectName("detectNextButton")
        self.next_button.setEnabled(False)

        cards = QGridLayout()
        cards.addWidget(self.os_card, 0, 0)
        cards.addWidget(self.conda_card, 0, 1)
        cards.addWidget(self.gpu_card, 1, 0)
        cards.addWidget(self.disk_card, 1, 1)

        env_panel = QFrame()
        env_panel.setObjectName("condaEnvPanel")
        env_layout = QVBoxLayout(env_panel)
        env_layout.setContentsMargins(16, 14, 16, 14)
        env_layout.setSpacing(8)
        env_layout.addWidget(self.conda_envs_title_label)
        env_layout.addWidget(self.conda_envs_label)

        actions = QHBoxLayout()
        actions.addStretch(1)
        actions.addWidget(self.detect_button)
        actions.addWidget(self.next_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        layout.addWidget(self.title_label)
        layout.addWidget(self.summary_label)
        layout.addLayout(cards)
        layout.addWidget(env_panel)
        layout.addLayout(actions)
        layout.addStretch(1)

        self.next_button.clicked.connect(self.next_requested.emit)

    def set_snapshot(self, snapshot: EnvSnapshot) -> None:
        self.os_card.set_status(snapshot.os, text.STATUS_SUPPORTED if snapshot.is_windows_supported else text.STATUS_UNSUPPORTED)
        conda_value = snapshot.conda.version or text.STATUS_NOT_FOUND
        conda_detail = snapshot.conda.path or text.STATUS_CONDA_WILL_INSTALL
        self.conda_card.set_status(conda_value, conda_detail)
        self.conda_envs_label.setText(", ".join(snapshot.conda.envs) if snapshot.conda.envs else "未发现 Conda 环境")
        if snapshot.gpu:
            self.gpu_card.set_status(snapshot.gpu.name, f"CUDA {snapshot.gpu.cuda_runtime_max}, {snapshot.gpu.memory_mib} MiB")
        else:
            self.gpu_card.set_status(text.STATUS_CPU_MODE, text.STATUS_NO_NVIDIA)
        self.disk_card.set_status(f"{snapshot.disk_root} {snapshot.free_disk_gb:.1f} GB 可用", text.STATUS_USER_WORKSPACE)
        self.next_button.setEnabled(snapshot.is_windows_supported)

    def run_detection(self, detect_func=None) -> EnvSnapshot:
        if detect_func is None:
            from app.core.detector import detect_all

            detect_func = detect_all
        snapshot = detect_func()
        self.set_snapshot(snapshot)
        return snapshot
