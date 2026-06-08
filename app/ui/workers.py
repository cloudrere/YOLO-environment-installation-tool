from __future__ import annotations

from PyQt6.QtCore import QThread, pyqtSignal

from app.core.conda_manager import install_miniconda, remove_env
from app.core.errors import InstallError
from app.core.pipeline import Pipeline


class InstallWorker(QThread):
    line_emitted = pyqtSignal(str)
    step_changed = pyqtSignal(str, str)
    finished = pyqtSignal(bool, str)

    def __init__(self, config: dict, *, dry_run: bool = False, parent=None):
        super().__init__(parent)
        self.config = config
        self.dry_run = dry_run
        self.pipeline: Pipeline | None = None

    def run(self) -> None:
        self.pipeline = Pipeline(self.config, self.line_emitted.emit, self.step_changed.emit, self.finished.emit)
        if self.dry_run:
            for step in Pipeline.STEPS:
                setattr(self.pipeline, f"_do_{step}", lambda step=step: self.line_emitted.emit(f"dry-run {step}"))
        self.pipeline.run()

    def cancel(self) -> None:
        if self.pipeline is not None:
            self.pipeline.cancel()


class MinicondaInstallWorker(QThread):
    line_emitted = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, target_dir: str, parent=None):
        super().__init__(parent)
        self.target_dir = target_dir

    def run(self) -> None:
        try:
            conda_exe = install_miniconda(self.target_dir, self.line_emitted.emit)
        except InstallError as exc:
            self.finished.emit(False, str(exc))
            return
        except Exception as exc:
            self.finished.emit(False, str(exc))
            return
        self.finished.emit(True, conda_exe)


class RemoveEnvWorker(QThread):
    line_emitted = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, conda_exe: str, env_name: str, parent=None):
        super().__init__(parent)
        self.conda_exe = conda_exe
        self.env_name = env_name

    def run(self) -> None:
        try:
            self.line_emitted.emit(f"正在卸载环境：{self.env_name}")
            remove_env(self.conda_exe, self.env_name)
        except InstallError as exc:
            self.finished.emit(False, str(exc))
            return
        except Exception as exc:
            self.finished.emit(False, str(exc))
            return
        self.finished.emit(True, self.env_name)
