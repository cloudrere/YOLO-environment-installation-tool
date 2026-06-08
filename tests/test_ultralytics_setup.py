from app.core import ultralytics_setup
from app.utils.runner import CommandResult


def test_install_ultralytics_uses_official_upgrade_command(monkeypatch):
    calls = []

    monkeypatch.setattr(ultralytics_setup, "pip_install", lambda *args, **kwargs: calls.append((args, kwargs)))

    ultralytics_setup.install_ultralytics("python.exe")

    assert calls[0][0][0] == "python.exe"
    assert calls[0][0][1] == ["-U", "ultralytics"]


def test_predownload_weights_uses_weight_dir(monkeypatch, tmp_path):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        return CommandResult(0, "OK yolov8n.pt", 0)

    monkeypatch.setattr(ultralytics_setup, "run", fake_run)

    result = ultralytics_setup.predownload_weights("python.exe", ["yolov8n.pt"], str(tmp_path))

    assert result == {"yolov8n.pt": str(tmp_path / "yolov8n.pt")}
    assert calls[0][0][0:3] == ["python.exe", "-c", ultralytics_setup.PREDOWNLOAD_SCRIPT]
    assert calls[0][1]["env"]["YOLO_CONFIG_DIR"] == str(tmp_path)


def test_smoke_test_returns_true_and_creates_parent(monkeypatch, tmp_path):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return CommandResult(0, "ok", 0)

    monkeypatch.setattr(ultralytics_setup, "run", fake_run)
    out_path = tmp_path / "nested" / "result.jpg"

    assert ultralytics_setup.smoke_test("python.exe", "yolov8n.pt", "bus.jpg", str(out_path)) is True
    assert out_path.parent.exists()
    assert calls[0][0] == "python.exe"


def test_weight_name_builder_reads_model_data():
    weights = ultralytics_setup.weights_from_model_ids(["yolov8:n", "yolo11:s-seg", "rtdetr"])

    assert "yolov8n.pt" in weights
    assert "yolo11s-seg.pt" in weights
    assert "rtdetr-l.pt" in weights
