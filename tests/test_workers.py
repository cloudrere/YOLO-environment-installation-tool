from app.ui.workers import InstallWorker


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
