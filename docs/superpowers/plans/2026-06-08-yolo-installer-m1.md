# YOLO Installer M1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a tested M1 core chain for the Windows YOLO environment installer.

**Architecture:** Keep subprocess execution centralized in `app.utils.runner`, keep environment parsing pure and testable, and make the pipeline a synchronous coordinator that UI code can later wrap in a QThread. Use JSON data files for CUDA, model, and mirror contracts from the supplied implementation plan.

**Tech Stack:** Python 3.11, pytest, PyQt-ready package layout, Windows conda/pip subprocess commands.

---

### Task 1: Project Skeleton and Data

**Files:**
- Create: `app/__init__.py`
- Create: `app/core/__init__.py`
- Create: `app/utils/__init__.py`
- Create: `app/data/cuda_torch_map.json`
- Create: `app/data/yolo_models.json`
- Create: `app/data/mirrors.json`
- Create: `requirements.txt`
- Create: `build/requirements-dev.txt`
- Create: `README.md`

- [ ] Create package directories and JSON contracts from the source implementation plan.
- [ ] Commit with `chore: scaffold project data`.

### Task 2: Runner

**Files:**
- Create: `app/utils/runner.py`
- Test: `tests/test_runner.py`

- [ ] Write tests for echo output, line callbacks, non-string command rejection, and timeout.
- [ ] Run `pytest tests/test_runner.py -v` and confirm failures are from missing implementation.
- [ ] Implement `CommandResult` and `run`.
- [ ] Run `pytest tests/test_runner.py -v`.
- [ ] Commit with `feat: add subprocess runner`.

### Task 3: Detector Parsers and Snapshot

**Files:**
- Create: `app/core/detector.py`
- Create: `tests/fixtures/nvidia_smi_550.txt`
- Create: `tests/fixtures/nvidia_smi_legacy.txt`
- Create: `tests/fixtures/nvidia_smi_no_gpu.txt`
- Create: `tests/fixtures/conda_env_list.txt`
- Test: `tests/test_detector_parse.py`

- [ ] Write tests for `parse_nvidia_smi`, `parse_conda_env_list`, and mocked `detect_all`.
- [ ] Run `pytest tests/test_detector_parse.py -v` and confirm missing implementation failures.
- [ ] Implement dataclasses, parsers, and environment detection.
- [ ] Run `pytest tests/test_detector_parse.py -v`.
- [ ] Commit with `feat: detect system environment`.

### Task 4: CUDA Matcher

**Files:**
- Create: `app/core/cuda_matcher.py`
- Test: `tests/test_cuda_matcher.py`

- [ ] Write tests for CUDA 12.6, 12.4, 12.1, 11.8, 10.2 fallback, and no GPU CPU mode.
- [ ] Run `pytest tests/test_cuda_matcher.py -v` and confirm missing implementation failures.
- [ ] Implement `TorchPlan` and `choose`.
- [ ] Run `pytest tests/test_cuda_matcher.py -v`.
- [ ] Commit with `feat: choose torch build from cuda`.

### Task 5: State and Installer Helpers

**Files:**
- Create: `app/core/state.py`
- Create: `app/core/errors.py`
- Create: `app/core/conda_manager.py`
- Create: `app/core/pip_installer.py`
- Create: `app/core/jupyter_installer.py`
- Test: `tests/test_state.py`
- Test: `tests/test_install_helpers.py`

- [ ] Write tests for state save/load/clear/corruption and command construction for conda/pip/jupyter.
- [ ] Run focused tests and confirm missing implementation failures.
- [ ] Implement state and helper modules.
- [ ] Run focused tests.
- [ ] Commit with `feat: add install helpers and state`.

### Task 6: Ultralytics Helpers and Pipeline

**Files:**
- Create: `app/core/ultralytics_setup.py`
- Create: `app/core/pipeline.py`
- Test: `tests/test_ultralytics_setup.py`
- Test: `tests/test_pipeline_mock.py`

- [ ] Write tests for weight predownload command selection, smoke test behavior, pipeline step order, cancellation, and failure state.
- [ ] Run focused tests and confirm missing implementation failures.
- [ ] Implement ultralytics helper and pipeline.
- [ ] Run focused tests.
- [ ] Commit with `feat: orchestrate installer pipeline`.

### Task 7: CLI and Full Verification

**Files:**
- Create: `main.py`
- Modify: `README.md`

- [ ] Add a small CLI entrypoint for detection, torch-plan output, and dry-run pipeline.
- [ ] Run full `pytest -v`.
- [ ] Run `python main.py --dry-run --models yolov8n`.
- [ ] Commit with `feat: add m1 cli entrypoint`.
