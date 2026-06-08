from app.core import pipeline, state
from app.core.detector import CondaInfo, EnvSnapshot, GpuInfo
from app.utils.runner import CancelledCommand


def test_pipeline_runs_steps_in_order_and_saves_state(monkeypatch, tmp_path):
    saved = []
    events = []
    monkeypatch.setattr(state, "STATE_PATH", tmp_path / "state.json")
    monkeypatch.setattr(state, "save", lambda snapshot: saved.append(snapshot))

    def step(name):
        return lambda self: events.append(name)

    for name in pipeline.Pipeline.STEPS:
        monkeypatch.setattr(pipeline.Pipeline, f"_do_{name}", step(name))

    done = []
    pipe = pipeline.Pipeline({"env_name": "demo"}, events.append, lambda s, st: events.append(f"{s}:{st}"), lambda ok, msg: done.append((ok, msg)))

    pipe.run()

    assert done == [(True, "")]
    assert [item for item in events if item in pipeline.Pipeline.STEPS] == pipeline.Pipeline.STEPS[:5]
    assert "weights:skipped" in events
    assert "jupyter:skipped" in events
    assert "smoke:skipped" in events
    assert "shortcut:skipped" in events
    assert [snapshot.finished_steps[-1] for snapshot in saved] == pipeline.Pipeline.STEPS


def test_pipeline_cancel_stops_before_next_step(monkeypatch):
    events = []

    def cancel_on_detect(self):
        events.append("detect")
        self.cancel()

    monkeypatch.setattr(pipeline.Pipeline, "_do_detect", cancel_on_detect)
    for name in pipeline.Pipeline.STEPS[1:]:
        monkeypatch.setattr(pipeline.Pipeline, f"_do_{name}", lambda self: events.append("unexpected"))

    done = []
    pipe = pipeline.Pipeline({}, events.append, lambda s, st: events.append(f"{s}:{st}"), lambda ok, msg: done.append((ok, msg)))

    pipe.run()

    assert "unexpected" not in events
    assert done == [(False, "canceled")]


def test_pipeline_reports_failed_step(monkeypatch):
    events = []

    def fail(self):
        raise RuntimeError("boom")

    monkeypatch.setattr(pipeline.Pipeline, "_do_detect", fail)

    done = []
    pipe = pipeline.Pipeline({}, events.append, lambda s, st: events.append(f"{s}:{st}"), lambda ok, msg: done.append((ok, msg)))

    pipe.run()

    assert "detect:fail" in events
    assert done == [(False, "boom")]


def test_pipeline_uses_conda_from_detection_before_creating_env(monkeypatch, tmp_path):
    snapshot = EnvSnapshot(
        os="Windows 11",
        is_windows_supported=True,
        conda=CondaInfo(r"D:\Anaconda\Scripts\conda.exe", "conda 24", ["base"]),
        gpu=GpuInfo("RTX 4070", "550.78", 12282, "12.4"),
        disk_root="D:",
        free_disk_gb=88.5,
        mirror_reachable=True,
    )
    monkeypatch.setattr(pipeline.detector, "detect_all", lambda: snapshot)
    monkeypatch.setattr(pipeline.cuda_matcher, "choose", lambda *args: type("Plan", (), {"__dict__": {"spec": []}})())
    monkeypatch.setattr(pipeline.conda_manager, "find_existing_conda", lambda: None)
    monkeypatch.setattr(pipeline.conda_manager, "install_miniconda", lambda *args: (_ for _ in ()).throw(AssertionError("should not install conda")))
    created = []
    monkeypatch.setattr(
        pipeline.conda_manager,
        "create_env",
        lambda conda, env, py, on_line=None, cancel_token=None: created.append((conda, env, py)) or r"D:\Anaconda\envs\demo\python.exe",
    )
    for name in ["torch", "ultralytics", "weights", "jupyter", "smoke", "shortcut"]:
        monkeypatch.setattr(pipeline.Pipeline, f"_do_{name}", lambda self: None)
    monkeypatch.setattr(state, "STATE_PATH", tmp_path / "state.json")

    done = []
    pipe = pipeline.Pipeline(
        {"env_name": "demo", "python_version": "3.12", "install_dir": str(tmp_path)},
        lambda line: None,
        lambda step, status: None,
        lambda ok, msg: done.append((ok, msg)),
    )

    pipe.run()

    assert created == [(r"D:\Anaconda\Scripts\conda.exe", "demo", "3.12")]
    assert done == [(True, "")]


def test_pipeline_installs_miniconda_from_conda_root_when_no_conda_exists(monkeypatch, tmp_path):
    snapshot = EnvSnapshot(
        os="Windows 11",
        is_windows_supported=True,
        conda=CondaInfo(None, None, []),
        gpu=None,
        disk_root="D:",
        free_disk_gb=88.5,
        mirror_reachable=True,
    )
    conda_root = tmp_path / "Miniconda3"
    conda_exe = str(conda_root / "Scripts" / "conda.exe")
    calls = []
    monkeypatch.setattr(pipeline.detector, "detect_all", lambda: snapshot)
    monkeypatch.setattr(pipeline.cuda_matcher, "choose", lambda *args: type("Plan", (), {"__dict__": {"spec": []}})())
    monkeypatch.setattr(pipeline.conda_manager, "find_existing_conda", lambda: None)
    monkeypatch.setattr(
        pipeline.conda_manager,
        "install_miniconda",
        lambda target, on_line=None: calls.append(target) or conda_exe,
    )
    monkeypatch.setattr(
        pipeline.conda_manager,
        "create_env",
        lambda conda, env, py, on_line=None, cancel_token=None: str(conda_root / "envs" / env / "python.exe"),
    )
    for name in ["torch", "ultralytics", "weights", "jupyter", "smoke", "shortcut"]:
        monkeypatch.setattr(pipeline.Pipeline, f"_do_{name}", lambda self: None)
    monkeypatch.setattr(state, "STATE_PATH", tmp_path / "state.json")

    done = []
    pipe = pipeline.Pipeline(
        {"env_name": "demo", "python_version": "3.12", "conda_root": str(conda_root), "workspace": str(conda_root)},
        lambda line: None,
        lambda step, status: None,
        lambda ok, msg: done.append((ok, msg)),
    )

    pipe.run()

    assert calls == [str(conda_root)]
    assert pipe.conda_exe == conda_exe
    assert done == [(True, "")]


def test_pipeline_disables_pip_fallback_for_gpu_torch_plan(monkeypatch):
    calls = []
    pipe = pipeline.Pipeline(
        {
            "torch_plan": {
                "mode": "gpu",
                "spec": ["torch==2.5.1+cu124"],
                "index_url": "https://download.pytorch.org/whl/cu124",
                "extra_index_url": None,
            },
            "python_exe": "python.exe",
        },
        lambda line: None,
        lambda step, status: None,
        lambda ok, msg: None,
    )

    monkeypatch.setattr(pipeline.pip_installer, "pip_install", lambda *args, **kwargs: calls.append((args, kwargs)))

    pipe._do_torch()

    assert calls[0][1]["allow_fallback_indexes"] is False


def test_pipeline_marks_configured_steps_as_skipped(monkeypatch):
    events = []
    monkeypatch.setattr(pipeline.Pipeline, "_do_detect", lambda self: None)
    monkeypatch.setattr(pipeline.Pipeline, "_do_conda", lambda self: None)
    monkeypatch.setattr(pipeline.Pipeline, "_do_env", lambda self: None)
    monkeypatch.setattr(pipeline.Pipeline, "_do_torch", lambda self: (_ for _ in ()).throw(AssertionError("torch should be skipped")))
    monkeypatch.setattr(
        pipeline.Pipeline,
        "_do_ultralytics",
        lambda self: (_ for _ in ()).throw(AssertionError("ultralytics should be skipped")),
    )
    for name in ["weights", "jupyter", "smoke", "shortcut"]:
        monkeypatch.setattr(pipeline.Pipeline, f"_do_{name}", lambda self: None)
    monkeypatch.setattr(state, "save", lambda snapshot: None)

    pipe = pipeline.Pipeline(
        {"skip_torch": True, "skip_ultralytics": True, "weights": [], "install_jupyter": False, "smoke_test": False, "make_shortcut": False},
        lambda line: events.append(("line", line)),
        lambda step, status: events.append((step, status)),
        lambda ok, msg: events.append(("done", ok, msg)),
    )

    pipe.run()

    assert ("torch", "skipped") in events
    assert ("ultralytics", "skipped") in events
    assert ("jupyter", "skipped") in events
    assert ("smoke", "skipped") in events
    assert ("shortcut", "skipped") in events
    assert ("done", True, "") in events


def test_pipeline_cancel_during_env_step_reports_canceled(monkeypatch, tmp_path):
    snapshot = EnvSnapshot(
        os="Windows 11",
        is_windows_supported=True,
        conda=CondaInfo(r"D:\Anaconda\Scripts\conda.exe", "conda 24", ["base"]),
        gpu=None,
        disk_root="D:",
        free_disk_gb=88.5,
        mirror_reachable=True,
    )
    monkeypatch.setattr(pipeline.detector, "detect_all", lambda: snapshot)
    monkeypatch.setattr(pipeline.cuda_matcher, "choose", lambda *args: type("Plan", (), {"__dict__": {"spec": []}})())
    monkeypatch.setattr(state, "STATE_PATH", tmp_path / "state.json")
    events = []

    def cancel_inside_create_env(*args, **kwargs):
        pipe.cancel()
        assert kwargs["cancel_token"].is_cancelled()
        raise CancelledCommand("canceled")

    monkeypatch.setattr(pipeline.conda_manager, "create_env", cancel_inside_create_env)

    pipe = pipeline.Pipeline(
        {"env_name": "demo", "python_version": "3.12", "install_dir": str(tmp_path)},
        lambda line: None,
        lambda step, status: events.append((step, status)),
        lambda ok, msg: events.append(("done", ok, msg)),
    )

    pipe.run()

    assert ("env", "fail") not in events
    assert events[-1] == ("done", False, "canceled")
