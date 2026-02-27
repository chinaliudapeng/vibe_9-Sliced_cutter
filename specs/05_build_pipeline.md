# Core Module: Build & Deployment

## 1. Requirements
- The project must be structured so it can be packaged into a standalone executable using `PyInstaller`.
- No absolute local paths should be hardcoded; use `os.path` or `pathlib` for resolving internal assets (if any).

## 2. Build Commands
The codebase must support the following standard packaging commands:
- **Windows:** `pyinstaller -F -w main.py` (Generates standalone `.exe` without console).
- **macOS:** `pyinstaller -F -w main.py` (Generates `.app` bundle).

## 3. Post-Build
- The compiled executable should open cleanly without terminal windows on both operating systems.