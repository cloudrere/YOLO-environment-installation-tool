from app.core import ultralytics_setup


def test_install_ultralytics_uses_official_upgrade_command(monkeypatch):
    calls = []

    monkeypatch.setattr(ultralytics_setup, "pip_install", lambda *args, **kwargs: calls.append((args, kwargs)))

    ultralytics_setup.install_ultralytics("python.exe")

    assert calls[0][0][0] == "python.exe"
    assert calls[0][0][1] == ["-U", "ultralytics"]
