from pathlib import Path

from app.utils.checksum import sha256_file


def test_sha256_file_returns_hex_digest(tmp_path):
    sample = tmp_path / "sample.bin"
    sample.write_bytes(b"abc")

    assert sha256_file(sample) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_pyinstaller_spec_contains_gui_entry_and_data_files():
    spec = Path("build/build.spec").read_text(encoding="utf-8")

    assert "main.py" in spec
    assert "str(ROOT / \"main.py\")" in spec
    assert "str(ROOT / \"app/data\")" in spec
    assert "str(ROOT / \"app/ui/style.qss\")" in spec
    assert "YoloInstaller" in spec
    assert "app/data" in spec
    assert "app/ui/style.qss" in spec
    assert "console=False" in spec
    assert '"torch"' in spec
    assert '"ultralytics"' in spec


def test_release_script_builds_exe_and_checksum():
    script = Path("build/make_release.ps1").read_text(encoding="utf-8")

    assert "pyinstaller" in script.lower()
    assert "build.spec" in script
    assert "YoloInstaller.exe.sha256" in script
    assert "Get-FileHash" in script
