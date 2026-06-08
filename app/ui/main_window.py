from __future__ import annotations

from PyQt6.QtWidgets import QMainWindow, QTabWidget

from app.core.errors import InstallError
from app.core.cuda_matcher import choose
from app.core.conda_manager import remove_env
from app.core.detector import detect_all
from app.core.ultralytics_setup import smoke_test
from app.ui import text
from app.ui.pages.detect_page import DetectPage
from app.ui.pages.install_page import InstallPage
from app.ui.pages.select_page import SelectPage
from app.ui.workers import InstallWorker
from app.utils.paths import resource_path


class MainWindow(QMainWindow):
    def __init__(self, *, dry_run: bool = False):
        super().__init__()
        self.dry_run = dry_run
        self.worker: InstallWorker | None = None
        self.snapshot = None
        self.current_config: dict = {}
        self.setWindowTitle(text.APP_TITLE)
        self.resize(980, 680)

        self.tabs = QTabWidget()
        self.tabs.setObjectName("mainTabs")
        self.detect_page = DetectPage()
        self.select_page = SelectPage()
        self.install_page = InstallPage()
        self.tabs.addTab(self.detect_page, text.TAB_ENVIRONMENT)
        self.tabs.addTab(self.select_page, text.TAB_MODELS)
        self.tabs.addTab(self.install_page, text.TAB_INSTALL)
        self.setCentralWidget(self.tabs)

        self.detect_page.detect_button.clicked.connect(self.run_detection)
        self.detect_page.next_requested.connect(lambda: self.tabs.setCurrentWidget(self.select_page))
        self.select_page.install_requested.connect(self.start_install)
        self.install_page.cancel_button.clicked.connect(self.cancel_install)
        self.install_page.try_button.clicked.connect(self.run_preview)
        self.install_page.uninstall_button.clicked.connect(self.uninstall_environment)
        self._load_style()

    def _load_style(self) -> None:
        qss = resource_path("app/ui/style.qss")
        if qss.exists():
            self.setStyleSheet(qss.read_text(encoding="utf-8"))

    def run_detection(self) -> None:
        self.snapshot = self.detect_page.run_detection(detect_all)

    def start_install(self, config: dict) -> None:
        if self.snapshot is None:
            self.run_detection()
        plan = choose(self.snapshot.gpu, str(resource_path("app/data/cuda_torch_map.json")))
        config = {**config, "torch_plan": plan.__dict__}
        if self.snapshot.conda.path:
            config["conda_exe"] = self.snapshot.conda.path
        self.current_config = config
        self.install_page.uninstall_env_edit.setText(config.get("env_name", "yolo-env"))
        self.tabs.setCurrentWidget(self.install_page)
        self.worker = InstallWorker(config, dry_run=self.dry_run)
        self.worker.line_emitted.connect(self.install_page.append_log)
        self.worker.step_changed.connect(self.install_page.set_step)
        self.worker.finished.connect(self.install_page.set_finished)
        self.worker.start()

    def cancel_install(self) -> None:
        if self.worker is not None:
            self.worker.cancel()

    def run_preview(self) -> None:
        config = self.current_config
        weights = config.get("weights") or ["yolov8n.pt"]
        ok = smoke_test(
            config.get("python_exe", "python"),
            weights[0],
            config.get("smoke_image", "assets/bus.jpg"),
            config.get("smoke_output", "result.jpg"),
        )
        self.install_page.append_log(text.PREVIEW_OK if ok else text.PREVIEW_FAILED)

    def uninstall_environment(self) -> None:
        config = self.current_config
        env_name = self.install_page.uninstall_env_edit.text().strip() or config.get("env_name", "yolo-env")
        conda_exe = config.get("conda_exe") or (self.snapshot.conda.path if self.snapshot and self.snapshot.conda.path else "conda")
        try:
            remove_env(conda_exe, env_name)
        except InstallError as exc:
            self.install_page.append_log(f"卸载失败：{exc}")
            return
        self.install_page.append_log(f"{text.ENV_REMOVED}：{env_name}")
