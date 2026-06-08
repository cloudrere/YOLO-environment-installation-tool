from app.core.validation import has_non_ascii, install_path_notice, install_path_warning, safe_default_install_dir


def test_has_non_ascii_detects_chinese_path():
    assert has_non_ascii(r"C:\Users\用户\miniconda3") is True
    assert has_non_ascii(r"C:\YoloInstaller\miniconda3") is False


def test_safe_default_install_dir_uses_ascii_fallback_for_chinese_home():
    assert safe_default_install_dir(r"C:\Users\用户") == r"C:\YoloInstaller\miniconda3"


def test_install_path_warning_explains_fallback():
    warning = install_path_warning(r"C:\Users\用户\miniconda3")

    assert "中文" in warning
    assert r"C:\YoloInstaller\miniconda3" in warning


def test_install_path_warning_empty_for_ascii_path():
    assert install_path_warning(r"C:\YoloInstaller\miniconda3") == ""


def test_install_path_notice_suggests_non_c_drive():
    notice = install_path_notice(r"C:\YoloInstaller\workspace")

    assert "不建议安装到 C 盘" in notice
    assert "D:\\YoloWorkspace" in notice
    assert install_path_notice(r"D:\YoloWorkspace") == ""
