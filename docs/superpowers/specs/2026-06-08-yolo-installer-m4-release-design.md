# YOLO Installer M4 Release Design

## Scope

M4 adds repeatable Windows release packaging. It provides a PyInstaller spec, a PowerShell release script, SHA-256 checksum generation, a changelog, and tests that validate the release configuration without requiring a clean virtual machine.

M4 does not claim clean Win10/Win11 E2E completion. That remains a manual release gate because it requires separate machines.

## Architecture

`build/build.spec` is the PyInstaller source of truth and bundles `app/data` plus `app/ui/style.qss`. `build/make_release.ps1` invokes PyInstaller, writes `dist/YoloInstaller.exe.sha256`, and prints the release paths. `app.utils.checksum` provides a small Python checksum helper for tests and any future release automation.

## Verification

M4 is accepted when the release config tests pass, existing pytest and ruff checks pass, CLI dry-run still works, and `build/make_release.ps1` can produce `dist/YoloInstaller.exe` plus a checksum on this development machine.
