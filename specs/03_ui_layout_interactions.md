# Core Module: UI Layout & Interactions (PySide6)

## 1. Main Window Layout & Responsive Design
The main application window must be fully resizable by dragging its edges or corners. 
- **Layout Manager:** Use `QSplitter` (horizontal) to divide the left and right panels. This allows users to dynamically adjust the ratio between the workspace and the control panel. The default initial ratio should be approximately 7:3.
- **Left Panel (Workspace):**
  - Must use a responsive canvas (e.g., `QGraphicsView` or a custom `QWidget` with `paintEvent`).
  - When the main window is resized, the displayed original image should automatically scale to fit the available viewport while maintaining its aspect ratio (Aspect Ratio Kept).
  - 4 draggable guide lines (Top, Bottom, Left, Right) overlaying the image. Their positions must scale proportionally or recalculate correctly when the canvas resizes.
  - Visual indicator (semi-transparent red/black mask) showing the "center cross" that will be deleted.
- **Right Panel (Controls & Preview):**
  - Must have a `MinimumWidth` set so the controls do not get crushed when the window is scaled down.
  - 4 `QSpinBox` widgets for manual integer input (`Top`, `Bottom`, `Left`, `Right`).
  - A real-time Preview rendering the result from the Image Processing module. The preview area should also be responsive.

## 2. High-DPI & Resolution Adaptation
To ensure the tool looks crisp on both standard monitors and High-DPI displays (like Mac Retina or 4K Windows monitors with 150%+ scaling):
- The application must explicitly handle High-DPI scaling. (Note: While Qt6 handles this well by default, ensure the base `QApplication` is initialized to support crisp font and image rendering across mixed-DPI multi-monitor setups).
- **Image Rendering:** The canvas and preview areas should use high-quality anti-aliasing (e.g., `Qt.SmoothTransformation`) when scaling down large images to fit the screen, preventing pixelation.

## 3. Two-Way Binding & Synchronization
- **Drag -> Input:** Dragging a guide line on the canvas must instantly update the corresponding `QSpinBox` value (calculating the actual image pixel value, not the screen coordinate).
- **Input -> Drag:** Typing or using arrows in a `QSpinBox` must instantly move the corresponding guide line on the canvas to the correct scaled position.
- **Update Preview:** Any change (from drag or input) triggers a signal to regenerate and update the Preview image.

## 4. Constraints
- Guide lines cannot cross each other.
  - `left` must be strictly less than `W - right` (leaving at least 1 pixel).
  - `top` must be strictly less than `H - bottom` (leaving at least 1 pixel).
- `QSpinBox` maximum values must be clamped dynamically based on the current loaded image dimensions.