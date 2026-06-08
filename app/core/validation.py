from __future__ import annotations


ASCII_INSTALL_DIR = r"C:\YoloInstaller\miniconda3"


def has_non_ascii(path: str) -> bool:
    return any(ord(char) > 127 for char in path)


def safe_default_install_dir(home_dir: str) -> str:
    if has_non_ascii(home_dir):
        return ASCII_INSTALL_DIR
    return rf"{home_dir}\miniconda3"


def install_path_warning(path: str) -> str:
    if not has_non_ascii(path):
        return ""
    return f"Path contains non-ASCII characters. Use {ASCII_INSTALL_DIR} to avoid conda and wheel issues."

