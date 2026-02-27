# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A desktop GUI tool for game developers to visually configure 9-slice (9-patch) borders on UI images. It removes the redundant center cross and exports a memory-optimized, stitched image compatible with Unity and other game engines.

**Status:** Specification-driven project — specs are complete, implementation is pending.

## Tech Stack

- **Language:** Python 3.10+
- **GUI:** PySide6 (Qt for Python) — native cross-platform rendering
- **Image Processing:** Pillow (PIL) — pixel-level manipulation
- **Testing:** pytest
- **Packaging:** PyInstaller

## Planned Project Structure

```
main.py                    # Entry point
requirements.txt
core/
  image_processor.py       # Pillow-based 9-slice algorithm
ui/
  main_window.py           # PySide6 GUI (window, canvas, controls)
tests/
  test_image_processor.py
```

## Commands

Once the project is initialized:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py

# Run all tests
pytest

# Run a single test file
pytest tests/test_image_processor.py

# Run a single test by name
pytest tests/test_image_processor.py::test_function_name -v

# Build standalone executable
pyinstaller -F -w main.py
```

## Core Algorithm (specs/02_core_image_logic.md)

The 9-slice "Type B — Engine Standard" algorithm:
- **Input:** Source image + margins (top, bottom, left, right) in pixels
- **Process:** Extract 4 corners + 4 edge bands (trimmed to 1px) + 1 center pixel; remove the center cross
- **Output:** Stitched image of size `(left + 1 + right, top + 1 + bottom)`

The center cross removal means the output retains exactly 1-pixel-wide stretching bands rather than the full interior region.

## GUI Architecture (specs/03_ui_layout_interactions.md)

- **Main layout:** Horizontal `QSplitter` — left workspace 70%, right controls 30%
- **Left panel:** Responsive canvas (QGraphicsView or custom QWidget) with 4 draggable guide lines and a semi-transparent mask over the center cross region
- **Right panel:** Four `QSpinBox` controls (top/bottom/left/right margins) + real-time preview
- **Two-way binding:** Dragging guide lines updates spinboxes; changing spinboxes updates guide positions and preview
- **Constraints:** Guide lines cannot cross each other; spinbox limits are clamped dynamically
- **High-DPI:** Use `Qt.SmoothTransformation` for scaling

Use Qt Signal/Slot mechanism for all state synchronization between UI and image logic. Keep UI logic and image processing logic in separate modules.

## File I/O (specs/04_file_io.md)

- Drag-and-drop accepts `.png`, `.jpg`, `.jpeg`
- Open via `QFileDialog.getOpenFileName`
- Save (overwrite) requires `QMessageBox.warning` confirmation
- Save As via `QFileDialog.getSaveFileName`, defaulting to the source file's directory
- No hardcoded absolute paths — use `os.path` or `pathlib`

## Development Workflow (specs/06_development_workflow.md)

- **TDD:** Write pytest tests before or alongside implementation
- **Git commits:** Conventional commits — `feat:`, `fix:`, `refactor:`, `chore:`, `test:`
- **Phases:** Implementation follows the 6-phase plan in `PROMPT.md`; Phases 3 & 4 require human visual confirmation before proceeding
- **Cross-platform:** Code must compile and run on both Windows and macOS without source changes
