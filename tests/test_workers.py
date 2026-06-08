from app.ui import workers
from app.ui.workers import InstallWorker, MinicondaInstallWorker, RemoveEnvWorker


def test_install_worker_dry_run_emits_steps(qtbot):
    worker = InstallWorker({"weights": ["yolov8n.pt"]}, dry_run=True)
    steps = []
    done = []
    worker.step_changed.connect(lambda step, status: steps.append((step, status)))
    worker.finished.connect(lambda ok, message: done.append((ok, message)))

    with qtbot.waitSignal(worker.finished, timeout=3000):
        worker.start()

    assert ("detect", "running") in steps
    assert ("shortcut", "ok") in steps
    assert done == [(True, "")]


def test_miniconda_install_worker_emits_result(qtbot, monkeypatch, tmp_path):
    conda_exe = str(tmp_path / "Miniconda3" / "Scripts" / "conda.exe")
    calls = []
    monkeypatch.setattr(
        workers,
        "install_miniconda",
        lambda target_dir, on_line=None: calls.append(target_dir) or on_line("installing") or conda_exe,
    )
    worker = MinicondaInstallWorker(str(tmp_path / "Miniconda3"))
    lines = []
    done = []
    worker.line_emitted.connect(lines.append)
    worker.finished.connect(lambda ok, message: done.append((ok, message)))

    with qtbot.waitSignal(worker.finished, timeout=3000):
        worker.start()

    assert calls == [str(tmp_path / "Miniconda3")]
    assert lines == ["installing"]
    assert done == [(True, conda_exe)]


def test_remove_env_worker_emits_result(qtbot, monkeypatch):
    calls = []
    monkeypatch.setattr(workers, "remove_env", lambda conda, env: calls.append((conda, env)))
    worker = RemoveEnvWorker("conda.exe", "old-env")
    done = []
    worker.finished.connect(lambda ok, message: done.append((ok, message)))

    with qtbot.waitSignal(worker.finished, timeout=3000):
        worker.start()

    assert calls == [("conda.exe", "old-env")]
    assert done == [(True, "old-env")]
