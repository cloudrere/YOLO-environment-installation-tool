from __future__ import annotations

import sys
from pathlib import Path


def app_root() -> Path:
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        return Path(bundle_root)
    return Path(__file__).resolve().parents[2]


def resource_path(relative_path: str) -> Path:
    return app_root() / relative_path

