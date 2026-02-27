# Core Module: File I/O & System Integration

## 1. Drag and Drop (DND)
- The Main Window must implement `dragEnterEvent` and `dropEvent`.
- **Validation:** Only accept local files with valid image extensions (`.png`, `.jpg`, `.jpeg`).
- **Action:** Dropping a valid file immediately loads it into the Left Panel and resets the 4 margins to default values.

## 2. Open via Dialog
- Provide an "Open" button calling `QFileDialog.getOpenFileName`.
- Apply file filters for images.

## 3. Save Actions
- **Save (Overwrite):**
  - Triggers the image processing logic.
  - MUST prompt a `QMessageBox.warning` asking for confirmation before overwriting the original file.
  - Upon confirmation, saves the new image to `source_image_path`.
- **Save As:**
  - Calls `QFileDialog.getSaveFileName`.
  - Default directory is the source image's directory.
  - Saves the processed image to the user-specified path.