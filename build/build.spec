# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


ROOT = Path.cwd()
CONDA_PREFIX = Path(r"E:\software\ADeepLearning\Anaconda\envs\ultralytics")
CONDA_BIN = CONDA_PREFIX / "Library" / "bin"


a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=[
        (str(CONDA_BIN / "libssl-3-x64.dll"), "."),
        (str(CONDA_BIN / "libcrypto-3-x64.dll"), "."),
        (str(CONDA_BIN / "liblzma.dll"), "."),
    ],
    datas=[
        (str(ROOT / "app/data"), "app/data"),
        (str(ROOT / "app/ui/style.qss"), "app/ui"),
    ],
    hiddenimports=[
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "cv2",
        "matplotlib",
        "numpy",
        "opencv_python",
        "pandas",
        "polars",
        "scipy",
        "torch",
        "torchaudio",
        "torchvision",
        "ultralytics",
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="YoloInstaller",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
