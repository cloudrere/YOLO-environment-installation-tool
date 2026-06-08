# YOLO Installer

M1 builds the tested core chain for a Windows YOLO environment installer. The GUI and packaged `.exe` are planned for later milestones.

## Development

Use the existing Anaconda `ultralytics` environment:

```powershell
E:\software\ADeepLearning\Anaconda\envs\ultralytics\python.exe -m pytest -v
```

Run a dry pipeline:

```powershell
E:\software\ADeepLearning\Anaconda\envs\ultralytics\python.exe main.py --dry-run --models yolov8n
```

Launch the desktop UI in safe dry-run mode:

```powershell
E:\software\ADeepLearning\Anaconda\envs\ultralytics\python.exe main.py --gui --dry-run
```

## Recovery behavior

- Non-ASCII install/workspace paths are blocked in the GUI with a fallback suggestion: `C:\YoloInstaller\miniconda3`.
- Pip installs retry through configured fallback mirrors from `app/data/mirrors.json`.
- The install page exposes preview and uninstall actions after a successful run.
- Resumable install state is stored under the user profile by `app.core.state`.

## Release build

Build the Windows executable and checksum:

```powershell
powershell -ExecutionPolicy Bypass -File build\make_release.ps1
```

Expected outputs:

- `dist\YoloInstaller.exe`
- `dist\YoloInstaller.exe.sha256`

Before publishing, run the manual clean-machine gates from the implementation plan: one fresh Windows machine with NVIDIA GPU, one fresh Windows machine without NVIDIA GPU, and record the smoke-test result image.

The current development build excludes torch/ultralytics runtime packages from the installer executable. The executable installs and calls those packages inside the target conda environment instead. If PyInstaller reports optional missing DLL warnings, verify the built executable on a clean machine before publishing.
