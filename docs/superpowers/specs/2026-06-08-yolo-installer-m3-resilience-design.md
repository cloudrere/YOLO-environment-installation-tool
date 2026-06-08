# YOLO Installer M3 Resilience Design

## Scope

M3 hardens the installer experience around failures and cleanup. It adds resumable-state discovery, Chinese/non-ASCII path protection for install/workspace choices, pip mirror fallback, a smoke-test preview action, and a clean uninstall action for conda environments.

The GUI remains safe by default: dry-run mode still avoids real installs. Real destructive actions are isolated behind explicit button clicks and helper methods that can be tested with monkeypatches.

## Architecture

`app.core.validation` owns path safety rules and fallback path suggestions. `app.core.resume` converts persisted `InstallState` into a user-facing resume summary. `pip_installer` reads configured mirrors when retries are needed. `InstallPage` gains preview and uninstall controls, while `MainWindow` wires them to `ultralytics_setup.smoke_test` and `conda_manager.remove_env`.

## UX Direction

Errors should be actionable and close to the relevant control. Path warnings appear on the model-selection page before install begins. The install page exposes recovery actions: try a smoke preview after success and uninstall the created environment when cleanup is needed. Destructive actions are visually separate from the primary flow.

## Verification

M3 is accepted when tests cover path validation, mirror fallback command order, resume summaries, preview/uninstall UI hooks, and the full previous M1/M2 test suite still passes.
