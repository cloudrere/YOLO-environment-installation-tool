from PyQt6.QtCore import Qt

from app.core.detector import CondaInfo, EnvSnapshot, GpuInfo
from app.ui.main_window import MainWindow


def fake_snapshot():
    return EnvSnapshot(
        os="Windows 10",
        is_windows_supported=True,
        conda=CondaInfo("conda.exe", "conda 24", ["base"]),
        gpu=GpuInfo("RTX 4070", "550.78", 12282, "12.4"),
        free_disk_gb=50,
        mirror_reachable=True,
    )


def test_main_window_has_three_pages(qtbot, monkeypatch):
    monkeypatch.setattr("app.ui.main_window.detect_all", fake_snapshot)
    window = MainWindow(dry_run=True)
    qtbot.addWidget(window)

    assert window.tabs.count() == 3
    assert window.tabs.tabText(0) == "Environment"
    assert window.tabs.tabText(1) == "Models"
    assert window.tabs.tabText(2) == "Install"


def test_main_window_detect_next_moves_to_models(qtbot, monkeypatch):
    monkeypatch.setattr("app.ui.main_window.detect_all", fake_snapshot)
    window = MainWindow(dry_run=True)
    qtbot.addWidget(window)

    window.run_detection()
    qtbot.mouseClick(window.detect_page.next_button, Qt.MouseButton.LeftButton)

    assert window.tabs.currentWidget() is window.select_page


def test_main_window_preview_action_logs_result(qtbot, monkeypatch):
    monkeypatch.setattr("app.ui.main_window.detect_all", fake_snapshot)
    calls = []
    window = MainWindow(dry_run=True)
    qtbot.addWidget(window)
    window.current_config = {
        "python_exe": "python.exe",
        "weights": ["yolov8n.pt"],
        "smoke_image": "bus.jpg",
        "smoke_output": "result.jpg",
    }
    monkeypatch.setattr("app.ui.main_window.smoke_test", lambda *args: calls.append(args) or True)

    window.run_preview()

    assert calls
    assert "Preview succeeded" in window.install_page.log_view.toPlainText()


def test_main_window_uninstall_action_removes_env(qtbot, monkeypatch):
    monkeypatch.setattr("app.ui.main_window.detect_all", fake_snapshot)
    calls = []
    window = MainWindow(dry_run=True)
    qtbot.addWidget(window)
    window.current_config = {"conda_exe": "conda.exe", "env_name": "demo"}
    monkeypatch.setattr("app.ui.main_window.remove_env", lambda conda, env: calls.append((conda, env)))

    window.uninstall_environment()

    assert calls == [("conda.exe", "demo")]
    assert "Environment removed" in window.install_page.log_view.toPlainText()
