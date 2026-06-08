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
