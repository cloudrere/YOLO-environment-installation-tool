# YOLO Installer M1 Design

## Scope

Build the M1 core chain from the implementation plan: subprocess runner, environment parsing, CUDA-to-PyTorch matching, conda command helpers, pip install wrapper, ultralytics setup helpers, resumable state, and a synchronous pipeline that can be driven from CLI or UI later.

This milestone intentionally excludes the PyQt GUI, PyInstaller release packaging, live Miniconda download validation, and full clean-machine end-to-end testing. Those remain for later milestones after the core chain is testable.

## Architecture

The app package is split into focused modules. `app.utils.runner` is the only subprocess entrypoint. `app.core.detector` gathers environment facts and exposes pure parsers for tests. `app.core.cuda_matcher` selects a torch installation plan from JSON data. Installation helpers build explicit command lists and raise typed errors on non-zero exits. `app.core.pipeline` orchestrates steps synchronously and saves state after each successful step.

## Verification

M1 is accepted when pytest passes for parser, matcher, state, runner, installer helper, ultralytics helper, and mocked pipeline behavior using the Anaconda `ultralytics` environment Python.
