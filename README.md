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
