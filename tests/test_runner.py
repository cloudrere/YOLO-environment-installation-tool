import subprocess
import sys
import threading
import time

import pytest

from app.utils.runner import CancelledCommand, CancelToken, run


def test_run_captures_output_and_return_code():
    result = run([sys.executable, "-c", "print('hello')"])

    assert result.returncode == 0
    assert result.stdout == "hello"
    assert result.duration_sec >= 0


def test_run_emits_each_line():
    lines = []

    run([sys.executable, "-c", "print('a'); print('b')"], on_line=lines.append)

    assert lines == ["a", "b"]


def test_run_rejects_string_commands():
    with pytest.raises(TypeError, match="cmd must be a sequence"):
        run("echo no shell")


def test_run_raises_timeout():
    with pytest.raises(subprocess.TimeoutExpired):
        run([sys.executable, "-c", "import time; time.sleep(2)"], timeout=0.1)


def test_run_can_cancel_running_process():
    token = CancelToken()

    def cancel_soon():
        time.sleep(0.1)
        token.cancel()

    threading.Thread(target=cancel_soon, daemon=True).start()

    started = time.monotonic()
    with pytest.raises(CancelledCommand):
        run([sys.executable, "-c", "import time; time.sleep(5)"], cancel_token=token)

    assert time.monotonic() - started < 2
