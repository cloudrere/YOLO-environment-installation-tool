from __future__ import annotations

import os
import platform
import re
import shutil
from dataclasses import dataclass

from app.utils.runner import run


_RE_CUDA = re.compile(r"CUDA Version:\s+(\d+\.\d+)")
_RE_DRIVER = re.compile(r"Driver Version:\s+([\d.]+)")


@dataclass(frozen=True)
class GpuInfo:
    name: str
    driver: str
    memory_mib: int
    cuda_runtime_max: str


@dataclass(frozen=True)
class CondaInfo:
    path: str | None
    version: str | None
    envs: list[str]


@dataclass(frozen=True)
class EnvSnapshot:
    os: str
    is_windows_supported: bool
    conda: CondaInfo
    gpu: GpuInfo | None
    free_disk_gb: float
    mirror_reachable: bool


def parse_nvidia_smi(text: str) -> GpuInfo | None:
    cuda_match = _RE_CUDA.search(text)
    if not cuda_match:
        return None

    comma_lines = [line.strip() for line in text.splitlines() if "MiB" in line and "," in line]
    if comma_lines:
        name, driver, memory = [part.strip() for part in comma_lines[0].split(",")[:3]]
        return GpuInfo(name, driver, int(memory.split()[0]), cuda_match.group(1))

    driver_match = _RE_DRIVER.search(text)
    return GpuInfo("NVIDIA GPU", driver_match.group(1) if driver_match else "", 0, cuda_match.group(1))


def parse_conda_env_list(text: str) -> list[str]:
    envs: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        envs.append(stripped.replace("*", " ").split()[0])
    return envs


def _detect_conda() -> CondaInfo:
    conda = shutil.which("conda")
    if not conda:
        return CondaInfo(None, None, [])
    version = run([conda, "--version"]).stdout.strip() or None
    envs_result = run([conda, "env", "list"])
    return CondaInfo(conda, version, parse_conda_env_list(envs_result.stdout))


def _detect_gpu() -> GpuInfo | None:
    nvidia_smi = shutil.which("nvidia-smi")
    if not nvidia_smi:
        return None
    result = run([nvidia_smi])
    return parse_nvidia_smi(result.stdout)


def detect_all() -> EnvSnapshot:
    usage = shutil.disk_usage(os.path.expanduser("~"))
    system = platform.system()
    return EnvSnapshot(
        os=f"{system} {platform.release()}",
        is_windows_supported=system == "Windows" and platform.release() in {"10", "11"},
        conda=_detect_conda(),
        gpu=_detect_gpu(),
        free_disk_gb=round(usage.free / (1024**3), 2),
        mirror_reachable=True,
    )

