from __future__ import annotations

import json
from pathlib import Path

from app.core.errors import InstallError
from app.utils.paths import resource_path
from app.utils.runner import run


def pip_install(
    python_exe: str,
    specs: list[str],
    *,
    index_url: str,
    extra_index_url: str | None = None,
    retries: int = 3,
    on_line=None,
    mirrors_path: str = "app/data/mirrors.json",
) -> None:
    last_output = ""
    indexes = [index_url, *_fallback_indexes(mirrors_path, index_url)]
    for attempt in range(retries):
        current_index = indexes[min(attempt, len(indexes) - 1)]
        cmd = [python_exe, "-m", "pip", "install", "-i", current_index]
        if extra_index_url:
            cmd.extend(["--extra-index-url", extra_index_url])
        cmd.extend(specs)
        result = run(cmd, on_line=on_line)
        last_output = result.stdout
        if result.returncode == 0:
            return
    raise InstallError(f"pip install failed for {', '.join(specs)}: {last_output}")


def _fallback_indexes(mirrors_path: str, primary: str) -> list[str]:
    path = Path(mirrors_path)
    if not path.is_absolute():
        path = resource_path(mirrors_path)
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [item["url"] for item in data.get("pip", []) if item.get("url") != primary]
