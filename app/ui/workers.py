from __future__ import annotations

from PyQt6.QtCore import QThread, pyqtSignal

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

