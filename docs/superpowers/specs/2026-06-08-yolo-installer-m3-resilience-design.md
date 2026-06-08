# YOLO Installer M3 Resilience Design

M3 hardens the installer around recovery and cleanup.

The main resilience paths are:

- validate unsafe paths before installation starts
- keep long-running commands cancelable
- keep installer state resumable
- retry ordinary pip operations through configured mirrors
- keep CUDA PyTorch installation pinned to CUDA-specific sources
- provide cleanup through Conda environment removal

Errors should be actionable and close to the relevant control. The install page shows the failing step, appends the exact command output to the log, and keeps cleanup controls available.
