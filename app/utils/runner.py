from __future__ import annotations

import os
import queue
import subprocess
import threading
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass


CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    duration_sec: float


class CancelledCommand(RuntimeError):
    pass


class CancelToken:
    def __init__(self) -> None:
        self._event = threading.Event()

    def cancel(self) -> None:
        self._event.set()

    def is_cancelled(self) -> bool:
        return self._event.is_set()


def run(
    cmd: Sequence[str],
    *,
    cwd: str | None = None,
    env: dict | None = None,
    on_line: Callable[[str], None] | None = None,
    timeout: float | None = None,
    cancel_token: CancelToken | None = None,
) -> CommandResult:
    """Run a subprocess without opening a console window on Windows."""
    if isinstance(cmd, (str, bytes)) or not isinstance(cmd, Sequence):
        raise TypeError("cmd must be a sequence of strings")

    full_env = os.environ.copy()
    full_env["PYTHONIOENCODING"] = "utf-8"
    if env:
        full_env.update(env)

    started = time.monotonic()
    proc = subprocess.Popen(
        list(cmd),
        cwd=cwd,
        env=full_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    lines: queue.Queue[str | None] = queue.Queue()

    def read_stdout() -> None:
        assert proc.stdout is not None
        try:
            for raw_line in proc.stdout:
                lines.put(raw_line.rstrip("\r\n"))
        finally:
            lines.put(None)

    reader = threading.Thread(target=read_stdout, daemon=True)
    reader.start()
    chunks: list[str] = []
    try:
        while True:
            if cancel_token is not None and cancel_token.is_cancelled():
                proc.kill()
                raise CancelledCommand("canceled")
            elapsed = time.monotonic() - started
            if timeout is not None and elapsed > timeout:
                proc.kill()
                raise subprocess.TimeoutExpired(list(cmd), timeout)
            try:
                line = lines.get(timeout=0.05)
            except queue.Empty:
                if proc.poll() is not None and not reader.is_alive():
                    break
                continue
            if line is None:
                break
            chunks.append(line)
            if on_line is not None:
                on_line(line)
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        raise
    finally:
        if proc.poll() is None:
            proc.kill()
    return CommandResult(proc.returncode, "\n".join(chunks), time.monotonic() - started)
