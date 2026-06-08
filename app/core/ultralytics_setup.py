from __future__ import annotations

from app.core.pip_installer import pip_install


def install_ultralytics(python_exe: str, on_line=None, cancel_token=None) -> None:
    pip_install(
        python_exe,
        ["-U", "ultralytics"],
        index_url="https://pypi.tuna.tsinghua.edu.cn/simple",
        on_line=on_line,
        cancel_token=cancel_token,
    )
