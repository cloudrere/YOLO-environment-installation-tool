# YOLO Installer M1 Plan

M1 establishes the tested core chain for a Windows YOLO environment installer.

Scope:

- detect Windows, Conda, NVIDIA GPU, CUDA, disk, and mirror availability
- choose a compatible PyTorch install plan
- create a Conda environment with a selected Python version
- install PyTorch and Ultralytics
- optionally install Jupyter
- persist resumable installation state
- support cancellation and failure reporting

The implementation is environment-focused and does not manage downloadable assets.
