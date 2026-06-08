import main


def test_no_arguments_launches_gui(monkeypatch):
    calls = []
    monkeypatch.setattr(main.sys, "argv", ["YoloInstaller.exe"])
    monkeypatch.setattr(main, "run_gui", lambda *, dry_run: calls.append(dry_run) or 0)

    assert main.main() == 0
    assert calls == [False]


def test_dry_run_without_gui_keeps_cli_mode(monkeypatch):
    calls = []
    monkeypatch.setattr(main.sys, "argv", ["YoloInstaller.exe", "--dry-run"])
    monkeypatch.setattr(main, "run_gui", lambda *, dry_run: calls.append(dry_run) or 0)
    monkeypatch.setattr(main, "detect_all", lambda: type("Snapshot", (), {"gpu": None, "__dict__": {}})())
    monkeypatch.setattr(main, "choose", lambda gpu, path: type("Plan", (), {"__dict__": {"mode": "cpu"}})())
    monkeypatch.setattr(main.Pipeline, "STEPS", [])

    assert main.main() == 0
    assert calls == []
