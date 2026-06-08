from __future__ import annotations

from app.core.pip_installer import pip_install


def install_jupyter(python_exe: str, *, index_url: str, on_line=None) -> None:
    pip_install(python_exe, ["jupyter", "ipykernel"], index_url=index_url, on_line=on_line)

