"""
Main window for the 9-slice cutter GUI tool.

Layout:
  - QSplitter (horizontal, 70:30)
    - Left:  CanvasWidget  — displays the source image + guide lines
    - Right: ControlPanel  — 4 QSpinBox controls + real-time preview
"""

from PySide6.QtWidgets import (
    QMainWindow, QSplitter, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QSpinBox, QPushButton,
    QSizePolicy, QFrame,
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QPainter, QColor, QPen

from core.image_processor import slice_image
from PIL import Image
from PIL.ImageQt import ImageQt


# ---------------------------------------------------------------------------
# Canvas widget (left panel)
# ---------------------------------------------------------------------------

class CanvasWidget(QWidget):
    """Displays the loaded source image and will host draggable guide lines."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(200, 200)

        self._source_pixmap: QPixmap | None = None
        self._img_w: int = 0
        self._img_h: int = 0

        # Margin values in image-pixel space
        self._top: int = 0
        self._bottom: int = 0
        self._left: int = 0
        self._right: int = 0

        # Displayed image rect inside the canvas (updated in paintEvent)
        self._display_rect_x: int = 0
        self._display_rect_y: int = 0
        self._display_scale: float = 1.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_image(self, image: Image.Image) -> None:
        """Load a PIL Image for display."""
        self._img_w, self._img_h = image.size
        # Convert to QPixmap via ImageQt
        qt_image = ImageQt(image.convert("RGBA"))
        self._source_pixmap = QPixmap.fromImage(qt_image)
        self.update()

    def set_margins(self, top: int, bottom: int, left: int, right: int) -> None:
        """Update guide-line positions from spinbox values."""
        self._top = top
        self._bottom = bottom
        self._left = left
        self._right = right
        self.update()

    # ------------------------------------------------------------------
    # Qt overrides
    # ------------------------------------------------------------------

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)

        # Background
        painter.fillRect(self.rect(), QColor(60, 60, 60))

        if self._source_pixmap is None:
            # Placeholder text
            painter.setPen(QColor(150, 150, 150))
            painter.drawText(
                self.rect(),
                Qt.AlignCenter,
                "打开或拖入图片\nOpen / Drop image here",
            )
            return

        # Scale image to fit canvas while preserving aspect ratio
        canvas_w = self.width()
        canvas_h = self.height()
        scale_x = canvas_w / self._img_w
        scale_y = canvas_h / self._img_h
        scale = min(scale_x, scale_y)
        self._display_scale = scale

        disp_w = int(self._img_w * scale)
        disp_h = int(self._img_h * scale)
        self._display_rect_x = (canvas_w - disp_w) // 2
        self._display_rect_y = (canvas_h - disp_h) // 2

        scaled = self._source_pixmap.scaled(
            QSize(disp_w, disp_h),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        painter.drawPixmap(self._display_rect_x, self._display_rect_y, scaled)

        # Draw guide lines and center-cross mask if image is loaded
        if self._img_w > 0 and self._img_h > 0:
            self._draw_guides(painter, disp_w, disp_h)

    def _draw_guides(self, painter: QPainter, disp_w: int, disp_h: int) -> None:
        ox, oy = self._display_rect_x, self._display_rect_y
        s = self._display_scale

        top_y    = oy + int(self._top * s)
        bottom_y = oy + int((self._img_h - self._bottom) * s)
        left_x   = ox + int(self._left * s)
        right_x  = ox + int((self._img_w - self._right) * s)

        # Semi-transparent center-cross mask
        mask_color = QColor(200, 0, 0, 70)
        painter.fillRect(left_x, oy,    right_x - left_x, top_y - oy,   mask_color)
        painter.fillRect(left_x, bottom_y, right_x - left_x, (oy + disp_h) - bottom_y, mask_color)
        painter.fillRect(ox, top_y,    left_x - ox,       bottom_y - top_y, mask_color)
        painter.fillRect(right_x, top_y, (ox + disp_w) - right_x, bottom_y - top_y, mask_color)
        # The center cross interior itself
        painter.fillRect(left_x, top_y, right_x - left_x, bottom_y - top_y, mask_color)

        # Guide lines
        pen = QPen(QColor(255, 80, 80), 1, Qt.DashLine)
        painter.setPen(pen)
        painter.drawLine(ox, top_y,    ox + disp_w, top_y)        # top
        painter.drawLine(ox, bottom_y, ox + disp_w, bottom_y)     # bottom
        painter.drawLine(left_x,  oy, left_x,  oy + disp_h)      # left
        painter.drawLine(right_x, oy, right_x, oy + disp_h)      # right


# ---------------------------------------------------------------------------
# Control panel (right panel)
# ---------------------------------------------------------------------------

class ControlPanel(QWidget):
    """Contains margin spinboxes and a preview of the sliced output."""

    margins_changed = Signal(int, int, int, int)  # top, bottom, left, right

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(220)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # --- Margin inputs ---
        margins_label = QLabel("切片边距 (Margins)")
        margins_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(margins_label)

        self._spinboxes: dict[str, QSpinBox] = {}
        for name in ("top", "bottom", "left", "right"):
            row = QHBoxLayout()
            lbl = QLabel(f"{name.capitalize()}:")
            lbl.setFixedWidth(55)
            spin = QSpinBox()
            spin.setMinimum(0)
            spin.setMaximum(9999)
            spin.setValue(0)
            spin.setObjectName(f"spin_{name}")
            spin.valueChanged.connect(self._on_margin_changed)
            self._spinboxes[name] = spin
            row.addWidget(lbl)
            row.addWidget(spin)
            layout.addLayout(row)

        layout.addSpacing(16)

        # --- Preview area ---
        preview_label_title = QLabel("预览 (Preview)")
        preview_label_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(preview_label_title)

        self._preview_label = QLabel()
        self._preview_label.setObjectName("preview_label")
        self._preview_label.setAlignment(Qt.AlignCenter)
        self._preview_label.setMinimumHeight(120)
        self._preview_label.setFrameShape(QFrame.StyledPanel)
        self._preview_label.setText("—")
        self._preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self._preview_label)

        layout.addStretch()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def top(self) -> int:
        return self._spinboxes["top"].value()

    @property
    def bottom(self) -> int:
        return self._spinboxes["bottom"].value()

    @property
    def left(self) -> int:
        return self._spinboxes["left"].value()

    @property
    def right(self) -> int:
        return self._spinboxes["right"].value()

    def set_image_limits(self, img_w: int, img_h: int) -> None:
        """Clamp spinbox maximums based on image dimensions."""
        max_h = max(0, img_h - 1)
        max_w = max(0, img_w - 1)
        self._spinboxes["top"].setMaximum(max_h)
        self._spinboxes["bottom"].setMaximum(max_h)
        self._spinboxes["left"].setMaximum(max_w)
        self._spinboxes["right"].setMaximum(max_w)

    def reset_values(self) -> None:
        """Reset all spinboxes to 0."""
        for spin in self._spinboxes.values():
            spin.blockSignals(True)
            spin.setValue(0)
            spin.blockSignals(False)
        self.margins_changed.emit(0, 0, 0, 0)

    def set_margin_values(self, top: int, bottom: int, left: int, right: int) -> None:
        """Programmatically set all four margins (blocks intermediate signals)."""
        for name, val in zip(("top", "bottom", "left", "right"), (top, bottom, left, right)):
            self._spinboxes[name].blockSignals(True)
            self._spinboxes[name].setValue(val)
            self._spinboxes[name].blockSignals(False)
        self.margins_changed.emit(top, bottom, left, right)

    def update_preview(self, result_image: Image.Image) -> None:
        """Render a sliced result image into the preview label."""
        qt_image = ImageQt(result_image.convert("RGBA"))
        pixmap = QPixmap.fromImage(qt_image)
        scaled = pixmap.scaled(
            self._preview_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self._preview_label.setPixmap(scaled)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_margin_changed(self) -> None:
        self.margins_changed.emit(
            self._spinboxes["top"].value(),
            self._spinboxes["bottom"].value(),
            self._spinboxes["left"].value(),
            self._spinboxes["right"].value(),
        )


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):
    """Top-level application window."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("9-Slice Cutter")
        self.resize(1100, 700)

        self._source_image: Image.Image | None = None

        # --- Splitter ---
        self._splitter = QSplitter(Qt.Horizontal)
        self._splitter.setObjectName("main_splitter")

        # Left: canvas
        self._canvas = CanvasWidget()
        self._canvas.setObjectName("canvas_widget")

        # Right: controls
        self._controls = ControlPanel()
        self._controls.setObjectName("control_panel")

        self._splitter.addWidget(self._canvas)
        self._splitter.addWidget(self._controls)

        # Set initial 70:30 ratio (sizes in pixels; will adjust on show)
        self._splitter.setStretchFactor(0, 7)
        self._splitter.setStretchFactor(1, 3)

        # Central widget wrapper
        central = QWidget()
        vbox = QVBoxLayout(central)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        # Toolbar row (open button)
        toolbar_row = QHBoxLayout()
        toolbar_row.setContentsMargins(8, 4, 8, 4)
        self._open_btn = QPushButton("打开图片 (Open)")
        self._open_btn.setObjectName("open_btn")
        self._open_btn.setFixedHeight(30)
        toolbar_row.addWidget(self._open_btn)
        toolbar_row.addStretch()

        self._save_btn = QPushButton("另存为 (Save As)")
        self._save_btn.setObjectName("save_btn")
        self._save_btn.setFixedHeight(30)
        self._save_btn.setEnabled(False)
        toolbar_row.addWidget(self._save_btn)

        vbox.addLayout(toolbar_row)
        vbox.addWidget(self._splitter)
        self.setCentralWidget(central)

        # --- Connect signals ---
        self._controls.margins_changed.connect(self._on_margins_changed)
        self._open_btn.clicked.connect(self._on_open_clicked)
        self._save_btn.clicked.connect(self._on_save_clicked)

        # Enable drag-and-drop
        self.setAcceptDrops(True)

    # ------------------------------------------------------------------
    # Public accessors (for testing)
    # ------------------------------------------------------------------

    @property
    def splitter(self) -> QSplitter:
        return self._splitter

    @property
    def canvas(self) -> CanvasWidget:
        return self._canvas

    @property
    def controls(self) -> ControlPanel:
        return self._controls

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_image(self, path: str) -> None:
        """Load a source image from disk and reset the UI."""
        image = Image.open(path)
        self._source_image = image
        self._canvas.set_image(image)
        self._controls.set_image_limits(*image.size)
        self._controls.reset_values()
        self._save_btn.setEnabled(True)
        self._update_preview()

    def _update_preview(self) -> None:
        """Regenerate the sliced preview from current margin values."""
        if self._source_image is None:
            return
        t = self._controls.top
        b = self._controls.bottom
        l = self._controls.left
        r = self._controls.right
        W, H = self._source_image.size
        # Guard: margins must leave at least 1px gap each axis
        if l + r >= W or t + b >= H:
            return
        try:
            result = slice_image(self._source_image, t, b, l, r)
            self._controls.update_preview(result)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_margins_changed(self, top: int, bottom: int, left: int, right: int) -> None:
        self._canvas.set_margins(top, bottom, left, right)
        self._update_preview()

    def _on_open_clicked(self) -> None:
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(
            self,
            "打开图片",
            "",
            "Images (*.png *.jpg *.jpeg)",
        )
        if path:
            self._load_image(path)

    def _on_save_clicked(self) -> None:
        if self._source_image is None:
            return
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        import os

        src_dir = ""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "另存为",
            src_dir,
            "PNG Image (*.png)",
        )
        if not path:
            return
        t = self._controls.top
        b = self._controls.bottom
        l = self._controls.left
        r = self._controls.right
        W, H = self._source_image.size
        if l + r >= W or t + b >= H:
            QMessageBox.warning(self, "错误", "边距设置无效，请检查后重试。")
            return
        result = slice_image(self._source_image, t, b, l, r)
        result.save(path)

    # ------------------------------------------------------------------
    # Drag-and-drop
    # ------------------------------------------------------------------

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        urls = event.mimeData().urls()
        if not urls:
            return
        path = urls[0].toLocalFile()
        if path.lower().endswith((".png", ".jpg", ".jpeg")):
            self._load_image(path)
