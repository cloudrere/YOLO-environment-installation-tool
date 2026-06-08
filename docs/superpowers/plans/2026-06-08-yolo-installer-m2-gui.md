# YOLO Installer M2 GUI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a tested PyQt6 three-page desktop GUI that safely drives the M1 pipeline in dry-run mode.

**Architecture:** Keep reusable widgets small, pages focused, and pipeline execution isolated in `InstallWorker`. The main window coordinates page transitions and builds config from page state. Real installation remains behind the existing M1 pipeline; M2 defaults to dry-run for safe GUI verification.

**Tech Stack:** Python 3.10/3.11, PyQt6, pytest-qt, pytest, ruff.

---

### Task 1: GUI Test Skeleton

**Files:**
- Create: `tests/test_ui_widgets.py`
- Create: `tests/test_ui_pages.py`
- Create: `tests/test_main_window.py`
- Create: `tests/test_workers.py`

- [ ] Write failing pytest-qt tests for widgets, pages, window navigation, and dry worker callbacks.
- [ ] Run `E:\software\ADeepLearning\Anaconda\envs\ultralytics\python.exe -m pytest tests/test_ui_widgets.py tests/test_ui_pages.py tests/test_main_window.py tests/test_workers.py -v`.
- [ ] Expected: import failures for missing `app.ui` modules.

### Task 2: Widgets

**Files:**
- Create: `app/ui/widgets/status_card.py`
- Create: `app/ui/widgets/model_card.py`
- Create: `app/ui/widgets/log_view.py`
- Create: `app/ui/widgets/__init__.py`

- [ ] Implement `StatusCard`, `ModelCard`, and `LogView`.
- [ ] Run focused widget tests and make them pass.

### Task 3: Pages

**Files:**
- Create: `app/ui/pages/detect_page.py`
- Create: `app/ui/pages/select_page.py`
- Create: `app/ui/pages/install_page.py`
- Create: `app/ui/pages/__init__.py`

- [ ] Implement detect, select, and install pages with stable object names.
- [ ] Run focused page tests and make them pass.

### Task 4: Worker and Main Window

**Files:**
- Create: `app/ui/workers.py`
- Create: `app/ui/main_window.py`
- Create: `app/ui/style.qss`
- Create: `app/ui/__init__.py`

- [ ] Implement `InstallWorker` with dry-run step callbacks.
- [ ] Implement `MainWindow` page transitions and config assembly.
- [ ] Run worker/window tests and make them pass.

### Task 5: Entry Point and Verification

**Files:**
- Modify: `main.py`
- Modify: `README.md`

- [ ] Add `--gui` launch path and keep CLI dry-run path working.
- [ ] Run full pytest, ruff, and CLI dry-run.
- [ ] Commit with `feat: add pyqt gui shell`.
