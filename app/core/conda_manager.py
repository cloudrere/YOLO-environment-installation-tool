from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from urllib import request as urlrequest

from app.core.errors import InstallError
from app.utils.paths import resource_path
from app.utils.runner import run


def find_existing_conda() -> str | None:
    return shutil.which("conda")


def install_miniconda(target_dir: str, on_line=None) -> str:
    target = Path(target_dir)
    url = _miniconda_installer_url()
    installer = Path(tempfile.gettempdir()) / "YoloInstaller-Miniconda3-latest-Windows-x86_64.exe"
    if on_line:
        on_line(f"正在下载 Miniconda：{url}")
    urlrequest.urlretrieve(url, str(installer))
    if on_line:
        on_line(f"正在安装 Miniconda 到：{target}")
    result = run(
        [
            str(installer),
            "/InstallationType=JustMe",
            "/RegisterPython=0",
            "/S",
            f"/D={target}",
        ],
        on_line=on_line,
    )
    if result.returncode != 0:
        raise InstallError(result.stdout or "Miniconda 安装失败")
    conda_exe = target / "Scripts" / "conda.exe"
    if on_line:
        on_line(f"Miniconda 安装完成：{conda_exe}")
    return str(conda_exe)


def _miniconda_installer_url() -> str:
    mirrors_path = resource_path("app/data/mirrors.json")
    data = json.loads(mirrors_path.read_text(encoding="utf-8"))
    return data["miniconda_installer"]


def write_condarc(channels: list[str], backup_dir: str) -> None:
    backup = Path(backup_dir)
    backup.mkdir(parents=True, exist_ok=True)
    condarc = Path.home() / ".condarc"
    if condarc.exists():
        shutil.copy2(condarc, backup / ".condarc.bak")
    lines = ["channels:", *[f"  - {channel}" for channel in channels], "show_channel_urls: true"]
    condarc.write_text("\n".join(lines) + "\n", encoding="utf-8")


def conda_root_from_executable(conda_exe: str | None) -> str | None:
    if not conda_exe:
        return None
    conda_path = Path(conda_exe)
    parts = [part.lower() for part in conda_path.parts]
    if len(parts) >= 3 and parts[-3:] == ["library", "bin", conda_path.name.lower()]:
        return str(conda_path.parents[2])
    if len(parts) >= 2 and parts[-2:] in [
        ["scripts", conda_path.name.lower()],
        ["condabin", conda_path.name.lower()],
    ]:
        return str(conda_path.parents[1])
    return str(conda_path.parent)


def env_python(conda_exe: str, env_name: str) -> str:
    root = Path(conda_root_from_executable(conda_exe) or Path(conda_exe).parent)
    return str(root / "envs" / env_name / "python.exe")


def create_env(conda_exe: str, env_name: str, python_version: str = "3.10", on_line=None, cancel_token=None) -> str:
    result = run(
        [conda_exe, "create", "-y", "-n", env_name, f"python={python_version}"],
        on_line=on_line,
        cancel_token=cancel_token,
    )
    if result.returncode != 0:
        raise InstallError(result.stdout)
    return env_python(conda_exe, env_name)


def remove_env(conda_exe: str, env_name: str) -> None:
    result = run([conda_exe, "env", "remove", "-y", "-n", env_name])
    if result.returncode != 0:
        raise InstallError(result.stdout)
