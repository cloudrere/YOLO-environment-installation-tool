# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path


ROOT = Path.cwd()
CONDA_PREFIX = Path(os.environ.get("CONDA_PREFIX", sys.prefix))
CONDA_BIN = CONDA_PREFIX / "Library" / "bin"

conda_binaries = [
    (str(path), ".")
    for path in (
        CONDA_BIN / "libssl-3-x64.dll",
        CONDA_BIN / "libcrypto-3-x64.dll",
        CONDA_BIN / "liblzma.dll",
    )
    if path.exists()
]


a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=conda_binaries,
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
