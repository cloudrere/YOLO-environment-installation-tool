# YOLO Installer M4 Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add repeatable PyInstaller release packaging with checksum output and release documentation.

**Architecture:** Keep build configuration in `build/`, keep checksum logic in a tiny tested utility, and keep generated release artifacts ignored under `dist/`. The PowerShell script is the user-facing release command.

**Tech Stack:** PyInstaller, PowerShell, Python hashlib, pytest, ruff.

---

### Task 1: Release Config Tests

**Files:**
- Create: `tests/test_release_config.py`

- [ ] Write failing tests for `build/build.spec`, `build/make_release.ps1`, and checksum helper behavior.
- [ ] Run focused tests and confirm failures for missing files/helper.

### Task 2: Checksum Helper

**Files:**
- Create: `app/utils/checksum.py`

- [ ] Implement `sha256_file(path) -> str`.
- [ ] Run focused checksum test.

### Task 3: PyInstaller Spec and Script

**Files:**
- Create: `build/build.spec`
- Create: `build/make_release.ps1`

- [ ] Add one-file windowed PyInstaller config for `main.py --gui`.
- [ ] Add release script that cleans output, invokes PyInstaller, and writes `.sha256`.
- [ ] Run release config tests.

### Task 4: Docs and Verification

**Files:**
- Create: `CHANGELOG.md`
- Modify: `README.md`

- [ ] Document release command and manual E2E gates.
- [ ] Run full pytest, ruff, CLI dry-run, and release script.
- [ ] Commit with `feat: add release packaging`.
