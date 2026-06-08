from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QGridLayout, QPushButton, QVBoxLayout, QWidget

from app.core.detector import EnvSnapshot
from app.ui import text
from app.ui.widgets.status_card import StatusCard


class DetectPage(QWidget):
    next_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("detectPage")
        self.os_card = StatusCard(text.LABEL_OS, text.STATUS_NOT_CHECKED)
        self.conda_card = StatusCard(text.LABEL_CONDA, text.STATUS_NOT_CHECKED)
        self.gpu_card = StatusCard(text.LABEL_GPU, text.STATUS_NOT_CHECKED)
        self.disk_card = StatusCard(text.LABEL_DISK, text.STATUS_NOT_CHECKED)
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

        layout = QVBoxLayout(self)
        layout.addLayout(cards)
        layout.addWidget(self.detect_button)
        layout.addWidget(self.next_button)
        layout.addStretch(1)

        self.next_button.clicked.connect(self.next_requested.emit)

    def set_snapshot(self, snapshot: EnvSnapshot) -> None:
        self.os_card.set_status(snapshot.os, text.STATUS_SUPPORTED if snapshot.is_windows_supported else text.STATUS_UNSUPPORTED)
        conda_value = snapshot.conda.version or text.STATUS_NOT_FOUND
        conda_detail = snapshot.conda.path or text.STATUS_CONDA_WILL_INSTALL
        self.conda_card.set_status(conda_value, conda_detail)
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
