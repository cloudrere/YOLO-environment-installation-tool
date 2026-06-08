from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


STATE_PATH = Path.home() / ".yolo_installer" / "state.json"


@dataclass(frozen=True)
class InstallState:
    started_at: str
    finished_steps: list[str]
    config: dict
    last_error: str | None = None


def load() -> InstallState | None:
    if not STATE_PATH.exists():
        return None
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        return InstallState(
            started_at=data["started_at"],
            finished_steps=list(data.get("finished_steps", [])),
            config=dict(data.get("config", {})),
            last_error=data.get("last_error"),
        )
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        return None


def save(s: InstallState) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(asdict(s), ensure_ascii=False, indent=2), encoding="utf-8")


def clear() -> None:
    try:
        STATE_PATH.unlink()
    except FileNotFoundError:
        return

