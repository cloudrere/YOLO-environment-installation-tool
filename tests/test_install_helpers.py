from app.core import conda_manager, jupyter_installer, pip_installer
from app.core.errors import InstallError
from app.utils.runner import CommandResult


def test_env_python_builds_windows_env_path():
    path = conda_manager.env_python(r"C:\Anaconda\Scripts\conda.exe", "yolo-env")

    assert path == r"C:\Anaconda\envs\yolo-env\python.exe"


def test_create_env_runs_conda_create(monkeypatch):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return CommandResult(0, "ok", 0)

    monkeypatch.setattr(conda_manager, "run", fake_run)

    python = conda_manager.create_env(r"C:\Anaconda\Scripts\conda.exe", "yolo-env", "3.11")

    assert calls[0] == [
        r"C:\Anaconda\Scripts\conda.exe",
        "create",
        "-y",
        "-n",
        "yolo-env",
        "python=3.11",
    ]
    assert python == r"C:\Anaconda\envs\yolo-env\python.exe"


def test_pip_install_raises_after_failed_attempts(monkeypatch):
    def fake_run(cmd, **kwargs):
        return CommandResult(1, "failed", 0)

    monkeypatch.setattr(pip_installer, "run", fake_run)

    try:
        pip_installer.pip_install("python.exe", ["demo"], index_url="https://bad.example", retries=1)
    except InstallError as exc:
        assert "demo" in str(exc)
    else:
        raise AssertionError("InstallError not raised")


def test_pip_install_includes_extra_index(monkeypatch):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return CommandResult(0, "ok", 0)

    monkeypatch.setattr(pip_installer, "run", fake_run)

    pip_installer.pip_install(
        "python.exe",
        ["torch"],
        index_url="https://mirror.example",
        extra_index_url="https://extra.example",
    )

    assert "--extra-index-url" in calls[0]
    assert calls[0][-1] == "torch"


def test_pip_install_switches_to_fallback_mirrors(monkeypatch, tmp_path):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        if "https://fallback.example/simple" in cmd:
            return CommandResult(0, "ok", 0)
        return CommandResult(1, "failed", 0)

    mirrors = tmp_path / "mirrors.json"
    mirrors.write_text(
        '{"pip": [{"name": "Fallback", "url": "https://fallback.example/simple"}]}',
        encoding="utf-8",
    )
    monkeypatch.setattr(pip_installer, "run", fake_run)

    pip_installer.pip_install(
        "python.exe",
        ["demo"],
        index_url="https://bad.example/simple",
        retries=2,
        mirrors_path=str(mirrors),
    )

    assert calls[0][5] == "https://bad.example/simple"
    assert calls[1][5] == "https://fallback.example/simple"


def test_install_jupyter_invokes_pip(monkeypatch):
    calls = []
    monkeypatch.setattr(jupyter_installer, "pip_install", lambda *args, **kwargs: calls.append((args, kwargs)))

    jupyter_installer.install_jupyter("python.exe", index_url="https://mirror.example")

    assert calls[0][0][1] == ["jupyter", "ipykernel"]
