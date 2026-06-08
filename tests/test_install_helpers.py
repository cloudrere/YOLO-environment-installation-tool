from app.core import conda_manager, jupyter_installer, pip_installer
from app.core.errors import InstallError
from app.utils.runner import CommandResult


def test_env_python_builds_windows_env_path():
    path = conda_manager.env_python(r"C:\Anaconda\Scripts\conda.exe", "yolo-env")

    assert path == r"C:\Anaconda\envs\yolo-env\python.exe"


def test_env_python_builds_path_from_library_bin_conda_bat():
    path = conda_manager.env_python(r"D:\Apps\Anaconda3\Library\bin\conda.BAT", "yolo-env")

    assert path == r"D:\Apps\Anaconda3\envs\yolo-env\python.exe"


def test_conda_root_supports_common_windows_entrypoints():
    cases = [
        (r"C:\Users\alice\miniconda3\Scripts\conda.exe", r"C:\Users\alice\miniconda3"),
        (r"D:\Apps\Anaconda3\Library\bin\conda.bat", r"D:\Apps\Anaconda3"),
        (r"E:\Tools\miniconda3\condabin\conda.bat", r"E:\Tools\miniconda3"),
        (r"F:\PortableConda\conda.exe", r"F:\PortableConda"),
    ]

    for conda_exe, expected_root in cases:
        assert conda_manager.conda_root_from_executable(conda_exe) == expected_root


def test_env_python_uses_condabin_root():
    path = conda_manager.env_python(r"E:\Tools\miniconda3\condabin\conda.bat", "yolo-env")

    assert path == r"E:\Tools\miniconda3\envs\yolo-env\python.exe"


def test_create_env_runs_conda_create(monkeypatch):
    calls = []
    token = object()

    def fake_run(cmd, **kwargs):
        calls.append((cmd, kwargs))
        return CommandResult(0, "ok", 0)

    monkeypatch.setattr(conda_manager, "run", fake_run)

    python = conda_manager.create_env(r"C:\Anaconda\Scripts\conda.exe", "yolo-env", "3.11", cancel_token=token)

    assert calls[0][0] == [
        r"C:\Anaconda\Scripts\conda.exe",
        "create",
        "-y",
        "-n",
        "yolo-env",
        "python=3.11",
    ]
    assert calls[0][1]["cancel_token"] is token
    assert python == r"C:\Anaconda\envs\yolo-env\python.exe"


def test_install_miniconda_downloads_and_runs_silent_installer(monkeypatch, tmp_path):
    calls = []
    lines = []

    def fake_urlretrieve(url, filename):
        calls.append(("download", url, filename))
        return filename, None

    def fake_run(cmd, **kwargs):
        calls.append(("run", cmd, kwargs))
        return CommandResult(0, "installed", 0)

    monkeypatch.setattr(conda_manager.urlrequest, "urlretrieve", fake_urlretrieve)
    monkeypatch.setattr(conda_manager, "run", fake_run)

    conda_exe = conda_manager.install_miniconda(str(tmp_path / "Miniconda3"), lines.append)

    assert conda_exe == str(tmp_path / "Miniconda3" / "Scripts" / "conda.exe")
    assert calls[0][0] == "download"
    assert calls[0][1].endswith("Miniconda3-latest-Windows-x86_64.exe")
    assert calls[1][1] == [
        calls[0][2],
        "/InstallationType=JustMe",
        "/RegisterPython=0",
        "/S",
        f"/D={tmp_path / 'Miniconda3'}",
    ]
    assert "正在下载 Miniconda" in lines[0]
    assert "Miniconda 安装完成" in lines[-1]


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


def test_pip_install_can_disable_fallback_mirrors(monkeypatch, tmp_path):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return CommandResult(1, "no matching distribution", 0)

    mirrors = tmp_path / "mirrors.json"
    mirrors.write_text(
        '{"pip": [{"name": "Fallback", "url": "https://fallback.example/simple"}]}',
        encoding="utf-8",
    )
    monkeypatch.setattr(pip_installer, "run", fake_run)

    try:
        pip_installer.pip_install(
            "python.exe",
            ["torch==2.5.1+cu124"],
            index_url="https://download.pytorch.org/whl/cu124",
            retries=2,
            mirrors_path=str(mirrors),
            allow_fallback_indexes=False,
        )
    except InstallError:
        pass
    else:
        raise AssertionError("InstallError not raised")

    assert len(calls) == 2
    assert all("https://download.pytorch.org/whl/cu124" in call for call in calls)
    assert all("https://fallback.example/simple" not in call for call in calls)


def test_install_jupyter_invokes_pip(monkeypatch):
    calls = []
    monkeypatch.setattr(jupyter_installer, "pip_install", lambda *args, **kwargs: calls.append((args, kwargs)))

    jupyter_installer.install_jupyter("python.exe", index_url="https://mirror.example")

    assert calls[0][0][1] == ["jupyter", "ipykernel"]
