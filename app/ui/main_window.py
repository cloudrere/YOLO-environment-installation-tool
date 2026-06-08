from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import QMainWindow, QTabWidget

from app.core.cuda_matcher import choose
from app.core.detector import detect_all
from app.ui.pages.detect_page import DetectPage
from app.ui.pages.install_page import InstallPage
from app.ui.pages.select_page import SelectPage
from app.ui.workers import InstallWorker


class MainWindow(QMainWindow):
    def __init__(self, *, dry_run: bool = False):
        super().__init__()
        self.dry_run = dry_run
        self.worker: InstallWorker | None = None
        self.snapshot = None
        self.setWindowTitle("YOLO Installer")
        self.resize(980, 680)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("mainTabs")
        self.detect_page = DetectPage()
        self.select_page = SelectPage()
        self.install_page = InstallPage()
        self.tabs.addTab(self.detect_page, "Environment")
        self.tabs.addTab(self.select_page, "Models")
        self.tabs.addTab(self.install_page, "Install")
        self.setCentralWidget(self.tabs)

        self.detect_page.detect_button.clicked.connect(self.run_detection)
        self.detect_page.next_requested.connect(lambda: self.tabs.setCurrentWidget(self.select_page))
        self.select_page.install_requested.connect(self.start_install)
        self.install_page.cancel_button.clicked.connect(self.cancel_install)
        self._load_style()

    def _load_style(self) -> None:
        qss = Path("app/ui/style.qss")
        if qss.exists():
            self.setStyleSheet(qss.read_text(encoding="utf-8"))

    def run_detection(self) -> None:
        self.snapshot = self.detect_page.run_detection(detect_all)

    def start_install(self, config: dict) -> None:
        if self.snapshot is None:
            self.run_detection()
        plan = choose(self.snapshot.gpu, "app/data/cuda_torch_map.json")
        config = {**config, "torch_plan": plan.__dict__, "python_exe": "python", "conda_exe": "conda"}
        self.tabs.setCurrentWidget(self.install_page)
        self.worker = InstallWorker(config, dry_run=self.dry_run)
        self.worker.line_emitted.connect(self.install_page.append_log)
        self.worker.step_changed.connect(self.install_page.set_step)
        self.worker.finished.connect(self.install_page.set_finished)
        self.worker.start()

    def cancel_install(self) -> None:
        if self.worker is not None:
            self.worker.cancel()

