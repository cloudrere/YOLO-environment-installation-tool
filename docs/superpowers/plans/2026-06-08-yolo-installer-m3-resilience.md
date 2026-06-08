# YOLO Installer M3 Resilience Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add tested failure recovery, path validation, preview, and cleanup behavior to the YOLO installer.

**Architecture:** Keep pure validation and resume logic in core modules, keep installer command construction in existing helpers, and let the PyQt pages expose clear controls without embedding installation details. GUI actions call injectable methods so tests can verify behavior without touching real conda environments.

**Tech Stack:** Python, PyQt6, pytest, pytest-qt, ruff.

---

### Task 1: Core Resilience Helpers

**Files:**
- Create: `app/core/validation.py`
- Create: `app/core/resume.py`
- Test: `tests/test_validation.py`
- Test: `tests/test_resume.py`

- [ ] Write failing tests for non-ASCII path detection, fallback path choice, and resume summary formatting.
- [ ] Implement pure helpers.
- [ ] Run focused tests.

### Task 2: Pip Mirror Fallback

**Files:**
- Modify: `app/core/pip_installer.py`
- Test: `tests/test_install_helpers.py`

- [ ] Write failing test proving pip tries primary mirror then configured fallback mirrors.
- [ ] Implement mirror loading from `app/data/mirrors.json`.
- [ ] Run focused tests.

### Task 3: GUI Recovery Controls

**Files:**
- Modify: `app/ui/pages/select_page.py`
- Modify: `app/ui/pages/install_page.py`
- Modify: `app/ui/main_window.py`
- Test: `tests/test_ui_pages.py`
- Test: `tests/test_main_window.py`

- [ ] Write failing tests for path warning, preview action, and uninstall action.
- [ ] Implement controls and injectable hooks.
- [ ] Run focused UI tests.

### Task 4: Documentation and Verification

**Files:**
- Modify: `README.md`

- [ ] Document M3 recovery behavior.
- [ ] Run full pytest, ruff, and CLI dry-run.
- [ ] Commit with `feat: harden installer recovery paths`.
