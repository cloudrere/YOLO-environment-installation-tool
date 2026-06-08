from __future__ import annotations

from datetime import datetime

from app.core import conda_manager, cuda_matcher, detector, jupyter_installer, pip_installer, state, ultralytics_setup
from app.core.state import InstallState


class Pipeline:
    STEPS = ["detect", "conda", "env", "torch", "ultralytics", "weights", "jupyter", "smoke", "shortcut"]

    def __init__(self, config: dict, on_line, on_step, on_done):
        self.config = config
        self.on_line = on_line
        self.on_step = on_step
        self.on_done = on_done
        self._cancelled = False
        self._finished_steps: list[str] = []
        self._current = ""
        self.snapshot = None
        self.conda_exe = None
        self.python_exe = config.get("python_exe")

    def cancel(self) -> None:
        self._cancelled = True

    def run(self) -> None:
        try:
            for step in self.STEPS:
                if self._cancelled:
                    self.on_done(False, "canceled")
                    return
                self._current = step
                self.on_step(step, "running")
                getattr(self, f"_do_{step}")()
                self.on_step(step, "ok")
                self._finished_steps.append(step)
                state.save(self._snapshot())
            self.on_done(True, "")
        except Exception as exc:
            if self._current:
                self.on_step(self._current, "fail")
            state.save(self._snapshot(str(exc)))
            self.on_done(False, str(exc))

    def _snapshot(self, last_error: str | None = None) -> InstallState:
        return InstallState(
            datetime.now().isoformat(timespec="seconds"),
            list(self._finished_steps),
            self.config,
            last_error,
        )

    def _do_detect(self) -> None:
        self.snapshot = detector.detect_all()
        self.config["torch_plan"] = cuda_matcher.choose(self.snapshot.gpu, "app/data/cuda_torch_map.json").__dict__

    def _do_conda(self) -> None:
        self.conda_exe = self.config.get("conda_exe") or conda_manager.find_existing_conda()
        if not self.conda_exe:
            self.conda_exe = conda_manager.install_miniconda(self.config["install_dir"], self.on_line)

    def _do_env(self) -> None:
        if not self.python_exe:
            self.python_exe = conda_manager.create_env(
                self.conda_exe,
                self.config.get("env_name", "yolo-env"),
                self.config.get("python_version", "3.10"),
                self.on_line,
            )

    def _do_torch(self) -> None:
        plan = self.config["torch_plan"]
        pip_installer.pip_install(
            self.python_exe,
            list(plan["spec"]),
            index_url=plan["index_url"],
            extra_index_url=plan.get("extra_index_url"),
            on_line=self.on_line,
        )

    def _do_ultralytics(self) -> None:
        ultralytics_setup.install_ultralytics(self.python_exe, self.on_line)

    def _do_weights(self) -> None:
        weights = self.config.get("weights", [])
        if weights:
            ultralytics_setup.predownload_weights(
                self.python_exe,
                weights,
                self.config.get("weight_dir", self.config.get("workspace", ".")),
                self.on_line,
            )

    def _do_jupyter(self) -> None:
        if self.config.get("install_jupyter", False):
            jupyter_installer.install_jupyter(
                self.python_exe,
                index_url=self.config.get("pip_mirror", "https://pypi.tuna.tsinghua.edu.cn/simple"),
                on_line=self.on_line,
            )

    def _do_smoke(self) -> None:
        if self.config.get("smoke_test", False):
            ultralytics_setup.smoke_test(
                self.python_exe,
                self.config["weights"][0],
                self.config["smoke_image"],
                self.config["smoke_output"],
            )

    def _do_shortcut(self) -> None:
        if self.config.get("make_shortcut", False):
            self.on_line("shortcut creation will be implemented in GUI milestone")

