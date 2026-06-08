from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from app.core.detector import GpuInfo


@dataclass(frozen=True)
class TorchPlan:
    mode: str
    cuda_tag: str | None
    spec: list[str]
    index_url: str
    extra_index_url: str | None = None


def _version_tuple(value: str) -> tuple[int, int]:
    if not re.fullmatch(r"\d+\.\d+", value):
        raise ValueError(f"Invalid CUDA version: {value}")
    major, minor = value.split(".")
    return int(major), int(minor)


def _cpu_plan(table: dict) -> TorchPlan:
    cpu = table["cpu"]
    return TorchPlan("cpu", None, list(cpu["spec"]), cpu["torch_index"], cpu.get("extra_index"))


def _cuda_tag_version(index_url: str) -> tuple[int, int] | None:
    tag = index_url.rstrip("/").split("/")[-1]
    match = re.fullmatch(r"cu(\d{2})(\d)", tag)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def choose(gpu: GpuInfo | None, table_path: str) -> TorchPlan:
    table = json.loads(Path(table_path).read_text(encoding="utf-8"))
    if gpu is None:
        return _cpu_plan(table)

    runtime = _version_tuple(gpu.cuda_runtime_max)
    for row in table["gpu"]:
        tag_version = _cuda_tag_version(row["torch_index"])
        if tag_version is not None and runtime >= tag_version:
            tag = row["torch_index"].rstrip("/").split("/")[-1]
            return TorchPlan("gpu", tag, list(row["spec"]), row["torch_index"])
    return _cpu_plan(table)
