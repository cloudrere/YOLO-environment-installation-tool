from __future__ import annotations

import shutil
from pathlib import Path

from app.core.errors import InstallError
from app.utils.runner import run


def find_existing_conda() -> str | None:
    return shutil.which("conda")


def install_miniconda(target_dir: str, on_line=None) -> str:
    raise InstallError("Miniconda download is not implemented in M1 dry core")


def write_condarc(channels: list[str], backup_dir: str) -> None:
    backup = Path(backup_dir)
    backup.mkdir(parents=True, exist_ok=True)
    condarc = Path.home() / ".condarc"
    if condarc.exists():
        shutil.copy2(condarc, backup / ".condarc.bak")
    lines = ["channels:", *[f"  - {channel}" for channel in channels], "show_channel_urls: true"]
    condarc.write_text("\n".join(lines) + "\n", encoding="utf-8")


def env_python(conda_exe: str, env_name: str) -> str:
    conda_path = Path(conda_exe)
    root = conda_path.parent.parent if conda_path.parent.name.lower() == "scripts" else conda_path.parent
    return str(root / "envs" / env_name / "python.exe")


def create_env(conda_exe: str, env_name: str, python_version: str = "3.10", on_line=None) -> str:
    result = run(
        [conda_exe, "create", "-y", "-n", env_name, f"python={python_version}"],
        on_line=on_line,
    )
    if result.returncode != 0:
        raise InstallError(result.stdout)
    return env_python(conda_exe, env_name)


def remove_env(conda_exe: str, env_name: str) -> None:
    result = run([conda_exe, "env", "remove", "-y", "-n", env_name])
    if result.returncode != 0:
        raise InstallError(result.stdout)
