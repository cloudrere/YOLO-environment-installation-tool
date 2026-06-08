from __future__ import annotations


ASCII_INSTALL_DIR = r"C:\YoloInstaller\miniconda3"
RECOMMENDED_WORKSPACE_DIR = r"D:\YoloWorkspace"


def has_non_ascii(path: str) -> bool:
    return any(ord(char) > 127 for char in path)


def safe_default_install_dir(home_dir: str) -> str:
    if has_non_ascii(home_dir):
        return ASCII_INSTALL_DIR
    return rf"{home_dir}\miniconda3"


def install_path_warning(path: str) -> str:
    if not has_non_ascii(path):
        return ""
    return f"路径包含中文或非 ASCII 字符。建议使用 {ASCII_INSTALL_DIR}，避免 Conda 和 wheel 安装异常。"


def install_path_notice(path: str) -> str:
    normalized = path.strip().replace("/", "\\")
    if len(normalized) >= 2 and normalized[1] == ":" and normalized[0].upper() == "C":
        return f"不建议安装到 C 盘，建议使用其他磁盘，例如 {RECOMMENDED_WORKSPACE_DIR}。"
    return ""
