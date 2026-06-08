# YOLO Installer M2 GUI Design

## Scope

M2 adds a PyQt6 desktop shell around the M1 core chain. It provides the three planned pages: environment detection, model selection, and install progress. The GUI can run the pipeline in dry-run mode for safe local validation and exposes the same callback boundaries that real installation will use later.

M2 intentionally does not perform a real environment install by default, does not package an `.exe`, and does not implement release screenshots. Those remain for later milestones.

## Architecture

`app.ui.main_window.MainWindow` owns a `QTabWidget` and coordinates page transitions. Pages are small widgets: `DetectPage` displays an `EnvSnapshot`, `SelectPage` builds weight selections from `yolo_models.json`, and `InstallPage` displays step status and bounded logs. `InstallWorker` wraps `Pipeline` in a `QThread` and supports a `dry_run` mode that exercises callbacks without installing packages.

## UX Direction

This is an operational installer, so the interface should be calm and dense rather than marketing-like. Use a neutral light theme, clear status cards, familiar form controls, visible disabled states, and a single primary next/start action per page. Text must fit within controls and all interactive controls should have stable names for tests and future accessibility labels.

## Verification

M2 is accepted when pytest-qt can instantiate each page, verify core interactions, run a dry worker without blocking the UI, and `main.py --dry-run --models yolov8:n` still works. Ruff must pass.
