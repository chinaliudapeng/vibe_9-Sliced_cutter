"""
Phase 4 headless tests: guide-line two-way binding and drag constraints.

All tests instantiate the window without show(), so they run in headless
CI environments.  A synthetic 100×80 RGBA image is loaded into the window
for every test to provide valid image dimensions.
"""

import sys
import pytest
from PIL import Image
from PySide6.QtWidgets import QApplication


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication(sys.argv)
    yield app


@pytest.fixture
def window(qapp):
    """Return a fully-wired MainWindow with a synthetic image loaded."""
    from ui.main_window import MainWindow

    win = MainWindow()
    # Load a synthetic 100×80 image directly (bypasses file I/O)
    img = Image.new("RGBA", (100, 80), (200, 200, 200, 255))
    win._source_image = img
    win._canvas.set_image(img)
    win._controls.set_image_limits(100, 80)
    win._controls.reset_values()
    yield win
    win.close()


# ---------------------------------------------------------------------------
# 1.  SpinBox → Canvas  (controls change → canvas guide positions update)
# ---------------------------------------------------------------------------

class TestSpinboxToCanvas:
    """Changing spinbox values propagates to canvas._top/bottom/left/right."""

    def test_top_spinbox_updates_canvas(self, window):
        window.controls.set_margin_values(10, 0, 0, 0)
        assert window.canvas._top == 10

    def test_bottom_spinbox_updates_canvas(self, window):
        window.controls.set_margin_values(0, 15, 0, 0)
        assert window.canvas._bottom == 15

    def test_left_spinbox_updates_canvas(self, window):
        window.controls.set_margin_values(0, 0, 20, 0)
        assert window.canvas._left == 20

    def test_right_spinbox_updates_canvas(self, window):
        window.controls.set_margin_values(0, 0, 0, 25)
        assert window.canvas._right == 25

    def test_all_four_margins_update_canvas(self, window):
        window.controls.set_margin_values(5, 10, 15, 20)
        assert window.canvas._top    == 5
        assert window.canvas._bottom == 10
        assert window.canvas._left   == 15
        assert window.canvas._right  == 20

    def test_reset_values_clears_canvas_margins(self, window):
        window.controls.set_margin_values(5, 10, 15, 20)
        window.controls.reset_values()
        assert window.canvas._top    == 0
        assert window.canvas._bottom == 0
        assert window.canvas._left   == 0
        assert window.canvas._right  == 0


# ---------------------------------------------------------------------------
# 2.  Canvas → SpinBox  (canvas drag signal → spinbox values update)
# ---------------------------------------------------------------------------

class TestCanvasToSpinbox:
    """Emitting canvas.margins_changed propagates to the spinboxes."""

    def test_signal_updates_top(self, window):
        window.canvas.margins_changed.emit(12, 0, 0, 0)
        assert window.controls.top == 12

    def test_signal_updates_bottom(self, window):
        window.canvas.margins_changed.emit(0, 18, 0, 0)
        assert window.controls.bottom == 18

    def test_signal_updates_left(self, window):
        window.canvas.margins_changed.emit(0, 0, 22, 0)
        assert window.controls.left == 22

    def test_signal_updates_right(self, window):
        window.canvas.margins_changed.emit(0, 0, 0, 30)
        assert window.controls.right == 30

    def test_signal_updates_all_four(self, window):
        window.canvas.margins_changed.emit(5, 8, 12, 18)
        assert window.controls.top    == 5
        assert window.controls.bottom == 8
        assert window.controls.left   == 12
        assert window.controls.right  == 18

    def test_no_circular_update(self, window):
        """Simulating a full drag (canvas state + signal) leaves both sides consistent."""
        # _process_drag sets canvas internals FIRST, then emits the signal.
        # We reproduce that here to verify no circular loop corrupts the state.
        window.canvas._top    = 3
        window.canvas._bottom = 7
        window.canvas._left   = 11
        window.canvas._right  = 17
        window.canvas.margins_changed.emit(3, 7, 11, 17)
        # Canvas state must be untouched (guard blocks redundant set_margins call)
        assert window.canvas._top    == 3
        assert window.canvas._bottom == 7
        assert window.canvas._left   == 11
        assert window.canvas._right  == 17
        # Spinboxes must be updated to match
        assert window.controls.top    == 3
        assert window.controls.bottom == 7
        assert window.controls.left   == 11
        assert window.controls.right  == 17


# ---------------------------------------------------------------------------
# 3.  Drag constraint enforcement  (via _process_drag)
# ---------------------------------------------------------------------------

class TestDragConstraints:
    """_process_drag enforces that opposing guide lines never cross."""

    def _setup_canvas(self, canvas, img_w=100, img_h=80,
                      top=0, bottom=0, left=0, right=0,
                      scale=1.0, ox=0, oy=0):
        canvas._img_w = img_w
        canvas._img_h = img_h
        canvas._top    = top
        canvas._bottom = bottom
        canvas._left   = left
        canvas._right  = right
        canvas._display_scale    = scale
        canvas._display_rect_x   = ox
        canvas._display_rect_y   = oy

    def test_top_drag_clamps_to_h_minus_bottom_minus_1(self, window):
        """Top guide cannot overlap or exceed (H - bottom)."""
        c = window.canvas
        self._setup_canvas(c, img_h=80, bottom=20)
        c._dragging = "top"
        c._process_drag(0, 70)          # img_y=70, max allowed = 80-20-1 = 59
        assert c._top == 59

    def test_top_drag_clamps_to_zero(self, window):
        c = window.canvas
        self._setup_canvas(c, img_h=80, bottom=0)
        c._dragging = "top"
        c._process_drag(0, -20)         # negative → clamp to 0
        assert c._top == 0

    def test_bottom_drag_cannot_cross_top(self, window):
        """Bottom guide cannot cross above the top guide."""
        c = window.canvas
        H = 80
        self._setup_canvas(c, img_h=H, top=30)
        c._dragging = "bottom"
        # Drag to img_y=25 (above top=30); pos forced to top+1=31
        # new_bottom = H - 31 = 49
        c._process_drag(0, 25)
        assert c._bottom == 49

    def test_bottom_drag_clamps_to_zero(self, window):
        """Dragging bottom guide to the very bottom gives bottom=0."""
        c = window.canvas
        H = 80
        self._setup_canvas(c, img_h=H, top=0)
        c._dragging = "bottom"
        c._process_drag(0, H)           # pos=80 → new_bottom = 80-80 = 0
        assert c._bottom == 0

    def test_left_drag_clamps_to_w_minus_right_minus_1(self, window):
        """Left guide cannot overlap or exceed (W - right)."""
        c = window.canvas
        self._setup_canvas(c, img_w=100, right=20)
        c._dragging = "left"
        c._process_drag(85, 0)          # img_x=85, max = 100-20-1 = 79
        assert c._left == 79

    def test_left_drag_clamps_to_zero(self, window):
        c = window.canvas
        self._setup_canvas(c, img_w=100, right=0)
        c._dragging = "left"
        c._process_drag(-10, 0)         # negative → clamp to 0
        assert c._left == 0

    def test_right_drag_cannot_cross_left(self, window):
        """Right guide cannot cross left of the left guide."""
        c = window.canvas
        W = 100
        self._setup_canvas(c, img_w=W, left=40)
        c._dragging = "right"
        # Drag to img_x=35 (left of left=40); pos forced to left+1=41
        # new_right = 100-41 = 59
        c._process_drag(35, 0)
        assert c._right == 59

    def test_right_drag_clamps_to_zero(self, window):
        """Dragging right guide to the far right gives right=0."""
        c = window.canvas
        W = 100
        self._setup_canvas(c, img_w=W, left=0)
        c._dragging = "right"
        c._process_drag(W, 0)           # pos=100 → new_right = 100-100 = 0
        assert c._right == 0


# ---------------------------------------------------------------------------
# 4.  Dynamic SpinBox maximum clamping
# ---------------------------------------------------------------------------

class TestDynamicSpinboxConstraints:
    """SpinBox maximums are updated in real-time as opposing margins change."""

    def test_top_max_decreases_when_bottom_set(self, window):
        window.controls.set_image_limits(100, 80)
        window.controls.set_margin_values(0, 30, 0, 0)
        # top.max = H - bottom - 1 = 80 - 30 - 1 = 49
        assert window.controls._spinboxes["top"].maximum() == 49

    def test_bottom_max_decreases_when_top_set(self, window):
        window.controls.set_image_limits(100, 80)
        window.controls.set_margin_values(20, 0, 0, 0)
        # bottom.max = H - top - 1 = 80 - 20 - 1 = 59
        assert window.controls._spinboxes["bottom"].maximum() == 59

    def test_left_max_decreases_when_right_set(self, window):
        window.controls.set_image_limits(100, 80)
        window.controls.set_margin_values(0, 0, 0, 25)
        # left.max = W - right - 1 = 100 - 25 - 1 = 74
        assert window.controls._spinboxes["left"].maximum() == 74

    def test_right_max_decreases_when_left_set(self, window):
        window.controls.set_image_limits(100, 80)
        window.controls.set_margin_values(0, 0, 35, 0)
        # right.max = W - left - 1 = 100 - 35 - 1 = 64
        assert window.controls._spinboxes["right"].maximum() == 64

    def test_maximums_symmetric_at_zero_margins(self, window):
        window.controls.set_image_limits(200, 100)
        window.controls.reset_values()
        spins = window.controls._spinboxes
        assert spins["top"].maximum()    == 99   # H-1
        assert spins["bottom"].maximum() == 99
        assert spins["left"].maximum()   == 199  # W-1
        assert spins["right"].maximum()  == 199


# ---------------------------------------------------------------------------
# 5.  Hit-test logic
# ---------------------------------------------------------------------------

class TestHitTest:
    """_hit_test returns the correct guide name based on screen coordinates."""

    def _setup_canvas(self, canvas):
        """Load a 100×80 image and force known display geometry."""
        img = Image.new("RGBA", (100, 80), (128, 128, 128, 255))
        canvas.set_image(img)
        canvas._top    = 10
        canvas._bottom = 10
        canvas._left   = 15
        canvas._right  = 15
        # Force a known display geometry (scale=2, origin at 0,0)
        canvas._display_scale  = 2.0
        canvas._display_rect_x = 0
        canvas._display_rect_y = 0

    def test_hit_top_guide(self, window):
        c = window.canvas
        self._setup_canvas(c)
        # top_y = 0 + int(10 * 2) = 20; hit within ±6px
        assert c._hit_test(50, 22) == "top"

    def test_hit_bottom_guide(self, window):
        c = window.canvas
        self._setup_canvas(c)
        # bottom_y = 0 + int((80-10) * 2) = 140
        assert c._hit_test(50, 138) == "bottom"

    def test_hit_left_guide(self, window):
        c = window.canvas
        self._setup_canvas(c)
        # left_x = 0 + int(15 * 2) = 30
        assert c._hit_test(32, 40) == "left"

    def test_hit_right_guide(self, window):
        c = window.canvas
        self._setup_canvas(c)
        # right_x = 0 + int((100-15) * 2) = 170
        assert c._hit_test(168, 40) == "right"

    def test_no_hit_outside_guides(self, window):
        c = window.canvas
        self._setup_canvas(c)
        # Far from any guide
        assert c._hit_test(80, 80) is None

    def test_no_hit_when_no_image(self, window):
        c = window.canvas
        c._source_pixmap = None
        c._img_w = 0
        c._img_h = 0
        assert c._hit_test(50, 50) is None
