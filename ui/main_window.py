"""
Main window for the 9-slice cutter GUI tool.

Layout:
  - QSplitter (horizontal, 70:30)
    - Left:  CanvasWidget  — displays the source image + draggable guide lines
    - Right: ControlPanel  — 4 QSpinBox controls + real-time preview
"""

from PySide6.QtWidgets import (
    QMainWindow, QSplitter, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QSpinBox, QPushButton,
    QSizePolicy, QFrame,
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QPainter, QColor, QPen, QCursor

from core.image_processor import slice_image
from PIL import Image
from PIL.ImageQt import ImageQt


# ---------------------------------------------------------------------------
# Canvas widget (left panel)
# ---------------------------------------------------------------------------

class CanvasWidget(QWidget):
    """Displays the loaded source image and hosts draggable guide lines."""

    # Emitted when guide lines are dragged; values in image-pixel space
    margins_changed = Signal(int, int, int, int)  # top, bottom, left, right

    _GRAB_PX = 6  # screen-pixel tolerance for hit-testing a guide line

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(200, 200)
        self.setMouseTracking(True)  # receive move events without held button

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

        # Dragging state: None or one of "top" | "bottom" | "left" | "right"
        self._dragging: str | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_image(self, image: Image.Image) -> None:
        """Load a PIL Image for display."""
        self._img_w, self._img_h = image.size
        qt_image = ImageQt(image.convert("RGBA"))
        self._source_pixmap = QPixmap.fromImage(qt_image)
        self.update()

    def set_margins(self, top: int, bottom: int, left: int, right: int) -> None:
        """Update guide-line positions from spinbox values (no signal emitted)."""
        self._top = top
        self._bottom = bottom
        self._left = left
        self._right = right
        self.update()

    # ------------------------------------------------------------------
    # Mouse events — guide-line dragging
    # ------------------------------------------------------------------

    def mousePressEvent(self, event) -> None:
        if self._source_pixmap is None or event.button() != Qt.LeftButton:
            return
        mx, my = event.position().x(), event.position().y()
        guide = self._hit_test(mx, my)
        if guide:
            self._dragging = guide
            self.update()

    def mouseMoveEvent(self, event) -> None:
        if self._source_pixmap is None:
            return
        mx, my = event.position().x(), event.position().y()
        if self._dragging:
            self._process_drag(mx, my)
        else:
            # Update cursor based on hover position
            guide = self._hit_test(mx, my)
            if guide in ("top", "bottom"):
                self.setCursor(Qt.SizeVerCursor)
            elif guide in ("left", "right"):
                self.setCursor(Qt.SizeHorCursor)
            else:
                self.unsetCursor()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton and self._dragging:
            self._dragging = None
            self.unsetCursor()
            self.update()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _guide_screen_coords(self):
        """Return screen coordinates of all four guide lines."""
        ox, oy = self._display_rect_x, self._display_rect_y
        s = self._display_scale
        top_y    = oy + int(self._top * s)
        bottom_y = oy + int((self._img_h - self._bottom) * s)
        left_x   = ox + int(self._left * s)
        right_x  = ox + int((self._img_w - self._right) * s)
        return top_y, bottom_y, left_x, right_x

    def _hit_test(self, mx: float, my: float) -> str | None:
        """Return the name of the guide line hit by (mx, my), or None."""
        if not self._img_w or not self._img_h or self._display_scale == 0:
            return None

        ox, oy = self._display_rect_x, self._display_rect_y
        s = self._display_scale
        disp_w = int(self._img_w * s)
        disp_h = int(self._img_h * s)

        top_y, bottom_y, left_x, right_x = self._guide_screen_coords()
        g = self._GRAB_PX

        img_left, img_right = ox, ox + disp_w
        img_top, img_bottom = oy, oy + disp_h

        # Horizontal guides — check within x-extent of image
        if img_left <= mx <= img_right:
            if abs(my - top_y) <= g:
                return "top"
            if abs(my - bottom_y) <= g:
                return "bottom"

        # Vertical guides — check within y-extent of image
        if img_top <= my <= img_bottom:
            if abs(mx - left_x) <= g:
                return "left"
            if abs(mx - right_x) <= g:
                return "right"

        return None

    def _process_drag(self, mx: float, my: float) -> None:
        """Compute new margin from current drag position and emit if changed."""
        ox, oy = self._display_rect_x, self._display_rect_y
        s = self._display_scale
        if s == 0:
            return

        W, H = self._img_w, self._img_h
        changed = False

        if self._dragging == "top":
            img_y = int((my - oy) / s)
            new_top = max(0, min(img_y, H - self._bottom - 1))
            if new_top != self._top:
                self._top = new_top
                changed = True

        elif self._dragging == "bottom":
            # Bottom guide sits at image-space position (H - bottom)
            pos = int((my - oy) / s)
            pos = max(self._top + 1, min(pos, H))
            new_bottom = max(0, H - pos)
            if new_bottom != self._bottom:
                self._bottom = new_bottom
                changed = True

        elif self._dragging == "left":
            img_x = int((mx - ox) / s)
            new_left = max(0, min(img_x, W - self._right - 1))
            if new_left != self._left:
                self._left = new_left
                changed = True

        elif self._dragging == "right":
            # Right guide sits at image-space position (W - right)
            pos = int((mx - ox) / s)
            pos = max(self._left + 1, min(pos, W))
            new_right = max(0, W - pos)
            if new_right != self._right:
                self._right = new_right
                changed = True

        if changed:
            self.margins_changed.emit(self._top, self._bottom, self._left, self._right)
            self.update()

    # ------------------------------------------------------------------
    # Qt overrides — painting
    # ------------------------------------------------------------------

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)

        # Background
        painter.fillRect(self.rect(), QColor(60, 60, 60))

        if self._source_pixmap is None:
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

        if self._img_w > 0 and self._img_h > 0:
            self._draw_guides(painter, disp_w, disp_h)

    def _draw_guides(self, painter: QPainter, disp_w: int, disp_h: int) -> None:
        ox, oy = self._display_rect_x, self._display_rect_y
        top_y, bottom_y, left_x, right_x = self._guide_screen_coords()

        # Semi-transparent center-cross mask (5 rectangles for the cross arms + center)
        mask_color = QColor(200, 0, 0, 70)
        painter.fillRect(left_x,  oy,        right_x - left_x, top_y - oy,             mask_color)
        painter.fillRect(left_x,  bottom_y,  right_x - left_x, (oy + disp_h) - bottom_y, mask_color)
        painter.fillRect(ox,      top_y,     left_x - ox,       bottom_y - top_y,       mask_color)
        painter.fillRect(right_x, top_y,     (ox + disp_w) - right_x, bottom_y - top_y, mask_color)
        painter.fillRect(left_x,  top_y,     right_x - left_x, bottom_y - top_y,        mask_color)

        # Guide lines — highlight active (being dragged) guide
        for name, coord, is_horiz in (
            ("top",    top_y,    True),
            ("bottom", bottom_y, True),
            ("left",   left_x,   False),
            ("right",  right_x,  False),
        ):
            color = QColor(255, 200, 0) if self._dragging == name else QColor(255, 80, 80)
            pen = QPen(color, 1, Qt.DashLine)
            painter.setPen(pen)
            if is_horiz:
                painter.drawLine(ox, coord, ox + disp_w, coord)
            else:
                painter.drawLine(coord, oy, coord, oy + disp_h)


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

        # Stored image dimensions for dynamic max clamping
        self._img_w: int = 0
        self._img_h: int = 0

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
        """Store image dimensions and clamp all spinbox maximums."""
        self._img_w = img_w
        self._img_h = img_h
        self._update_maximums()

    def reset_values(self) -> None:
        """Reset all spinboxes to 0."""
        for spin in self._spinboxes.values():
            spin.blockSignals(True)
            spin.setValue(0)
            spin.blockSignals(False)
        self._update_maximums()
        self.margins_changed.emit(0, 0, 0, 0)

    def set_margin_values(self, top: int, bottom: int, left: int, right: int) -> None:
        """Programmatically set all four margins (blocks intermediate signals)."""
        for name, val in zip(("top", "bottom", "left", "right"), (top, bottom, left, right)):
            self._spinboxes[name].blockSignals(True)
            self._spinboxes[name].setValue(val)
            self._spinboxes[name].blockSignals(False)
        self._update_maximums()
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
    # Internal helpers
    # ------------------------------------------------------------------

    def _update_maximums(self) -> None:
        """Clamp each spinbox maximum so that opposing guides cannot cross."""
        if self._img_w == 0 or self._img_h == 0:
            return
        W, H = self._img_w, self._img_h
        top    = self._spinboxes["top"].value()
        bottom = self._spinboxes["bottom"].value()
        left   = self._spinboxes["left"].value()
        right  = self._spinboxes["right"].value()
        self._spinboxes["top"].setMaximum(max(0, H - bottom - 1))
        self._spinboxes["bottom"].setMaximum(max(0, H - top - 1))
        self._spinboxes["left"].setMaximum(max(0, W - right - 1))
        self._spinboxes["right"].setMaximum(max(0, W - left - 1))

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_margin_changed(self) -> None:
        self._update_maximums()
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
        self._source_path: str | None = None  # path of the currently loaded file
        self._updating: bool = False  # guard against circular signal loops

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

        self._splitter.setStretchFactor(0, 7)
        self._splitter.setStretchFactor(1, 3)

        # Central widget wrapper
        central = QWidget()
        vbox = QVBoxLayout(central)
        vbox.setContentsMargins(10, 10, 10, 10)  # Edge margins: left=10px, bottom=10px per spec
        vbox.setSpacing(0)

        # Toolbar row
        toolbar_row = QHBoxLayout()
        toolbar_row.setContentsMargins(8, 4, 8, 4)
        self._open_btn = QPushButton("打开图片 (Open)")
        self._open_btn.setObjectName("open_btn")
        self._open_btn.setFixedHeight(30)
        toolbar_row.addWidget(self._open_btn)
        toolbar_row.addStretch()

        self._overwrite_btn = QPushButton("覆盖保存 (Save)")
        self._overwrite_btn.setObjectName("overwrite_btn")
        self._overwrite_btn.setFixedHeight(30)
        self._overwrite_btn.setEnabled(False)
        toolbar_row.addWidget(self._overwrite_btn)

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
        self._canvas.margins_changed.connect(self._on_canvas_margins_changed)
        self._open_btn.clicked.connect(self._on_open_clicked)
        self._overwrite_btn.clicked.connect(self._on_overwrite_save_clicked)
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
        self._source_path = path
        self._canvas.set_image(image)
        self._controls.set_image_limits(*image.size)
        self._controls.reset_values()
        self._overwrite_btn.setEnabled(True)
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
        """SpinBox → Canvas: update guide positions and refresh preview."""
        if self._updating:
            return
        self._canvas.set_margins(top, bottom, left, right)
        self._update_preview()

    def _on_canvas_margins_changed(self, top: int, bottom: int, left: int, right: int) -> None:
        """Canvas drag → SpinBox: update spinbox values without re-triggering canvas."""
        if self._updating:
            return
        self._updating = True
        self._controls.set_margin_values(top, bottom, left, right)
        self._updating = False
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

    def _on_overwrite_save_clicked(self) -> None:
        """Overwrite the original source file after user confirmation."""
        if self._source_image is None or self._source_path is None:
            return
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.warning(
            self,
            "覆盖保存",
            f"确认要覆盖原文件吗？\n{self._source_path}",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
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
        result.save(self._source_path)

    def _on_save_clicked(self) -> None:
        """Save As: prompt the user for a new file path."""
        if self._source_image is None:
            return
        import os
        from PySide6.QtWidgets import QFileDialog, QMessageBox

        default_dir = os.path.dirname(self._source_path) if self._source_path else ""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "另存为",
            default_dir,
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
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith((".png", ".jpg", ".jpeg")):
                    event.acceptProposedAction()
                    return

    def dropEvent(self, event) -> None:
        urls = event.mimeData().urls()
        if not urls:
            return
        path = urls[0].toLocalFile()
        if path.lower().endswith((".png", ".jpg", ".jpeg")):
            self._load_image(path)
