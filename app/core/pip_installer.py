from __future__ import annotations

from app.core.errors import InstallError
from app.utils.runner import run


def pip_install(
    python_exe: str,
    specs: list[str],
    *,
    index_url: str,
    extra_index_url: str | None = None,
    retries: int = 3,
    on_line=None,
) -> None:
    last_output = ""
    for _ in range(retries):
        cmd = [python_exe, "-m", "pip", "install", "-i", index_url]
        if extra_index_url:
            cmd.extend(["--extra-index-url", extra_index_url])
        cmd.extend(specs)
        result = run(cmd, on_line=on_line)
        last_output = result.stdout
        if result.returncode == 0:
            return
    raise InstallError(f"pip install failed for {', '.join(specs)}: {last_output}")

