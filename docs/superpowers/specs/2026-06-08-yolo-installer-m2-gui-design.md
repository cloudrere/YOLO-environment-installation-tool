# YOLO Installer M2 GUI Design

This GUI milestone defines a focused Windows desktop installer for creating a usable YOLO Python environment.

The application has three views:

- environment detection
- installation configuration
- installation progress and cleanup

The detection view renders operating system, Conda, GPU, CUDA, disk, and existing Conda environment information. The configuration view collects the target environment name, Python version, Conda root directory, and optional installation toggles. The progress view shows step status, logs, cancellation, and environment removal.

The GUI is intentionally environment-focused. It does not manage downloadable assets or bundled sample inference.
