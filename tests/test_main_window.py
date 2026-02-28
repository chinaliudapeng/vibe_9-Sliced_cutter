"""
Headless tests for the MainWindow GUI skeleton (Phase 3).

These tests instantiate the window without calling show(), so they can run
in CI environments without a display server.  On Windows/macOS a virtual
QApplication is sufficient; on headless Linux you would need a virtual
framebuffer (e.g. xvfb-run pytest ...).
"""

import sys
import pytest

# PySide6 requires a QApplication to exist before any widgets are created.
from PySide6.QtWidgets import QApplication, QSplitter, QSpinBox, QLabel, QPushButton

# Create / reuse a single QApplication for the whole test session.
@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication(sys.argv)
    yield app


@pytest.fixture
def window(qapp):
    """Return a MainWindow instance without showing it."""
    from ui.main_window import MainWindow
    win = MainWindow()
    yield win
    win.close()


# ---------------------------------------------------------------------------
# Structure tests
# ---------------------------------------------------------------------------

class TestMainWindowStructure:

    def test_window_title(self, window):
        assert "9-Slice" in window.windowTitle()

    def test_has_splitter(self, window):
        splitter = window.splitter
        assert splitter is not None
        assert isinstance(splitter, QSplitter)

    def test_splitter_has_two_children(self, window):
        assert window.splitter.count() == 2

    def test_canvas_widget_exists(self, window):
        from ui.main_window import CanvasWidget
        assert isinstance(window.canvas, CanvasWidget)

    def test_control_panel_exists(self, window):
        from ui.main_window import ControlPanel
        assert isinstance(window.controls, ControlPanel)

    def test_canvas_is_left_child(self, window):
        from ui.main_window import CanvasWidget
        assert isinstance(window.splitter.widget(0), CanvasWidget)

    def test_controls_are_right_child(self, window):
        from ui.main_window import ControlPanel
        assert isinstance(window.splitter.widget(1), ControlPanel)


# ---------------------------------------------------------------------------
# SpinBox tests
# ---------------------------------------------------------------------------

class TestSpinBoxes:

    def _get_spinboxes(self, window) -> list[QSpinBox]:
        return window.controls.findChildren(QSpinBox)

    def test_exactly_four_spinboxes(self, window):
        spins = self._get_spinboxes(window)
        assert len(spins) == 4

    def test_spinbox_names_present(self, window):
        names = {sb.objectName() for sb in self._get_spinboxes(window)}
        assert names == {"spin_top", "spin_bottom", "spin_left", "spin_right"}

    def test_spinbox_initial_values_zero(self, window):
        for sb in self._get_spinboxes(window):
            assert sb.value() == 0

    def test_spinbox_minimum_is_zero(self, window):
        for sb in self._get_spinboxes(window):
            assert sb.minimum() == 0


# ---------------------------------------------------------------------------
# Preview label tests
# ---------------------------------------------------------------------------

class TestPreviewLabel:

    def test_preview_label_exists(self, window):
        label = window.controls.findChild(QLabel, "preview_label")
        assert label is not None

    def test_preview_label_initial_text(self, window):
        label = window.controls.findChild(QLabel, "preview_label")
        assert label.text() == "—"


# ---------------------------------------------------------------------------
# Toolbar button tests
# ---------------------------------------------------------------------------

class TestToolbarButtons:

    def test_open_button_exists(self, window):
        btn = window.findChild(QPushButton, "open_btn")
        assert btn is not None

    def test_save_button_exists(self, window):
        btn = window.findChild(QPushButton, "save_btn")
        assert btn is not None

    def test_save_button_initially_disabled(self, window):
        btn = window.findChild(QPushButton, "save_btn")
        assert not btn.isEnabled()


# ---------------------------------------------------------------------------
# Margin API tests
# ---------------------------------------------------------------------------

class TestControlPanelAPI:

    def test_set_margin_values_updates_spinboxes(self, window):
        window.controls.set_margin_values(10, 20, 30, 40)
        assert window.controls.top == 10
        assert window.controls.bottom == 20
        assert window.controls.left == 30
        assert window.controls.right == 40

    def test_reset_values_zeroes_spinboxes(self, window):
        window.controls.set_margin_values(10, 20, 30, 40)
        window.controls.reset_values()
        assert window.controls.top == 0
        assert window.controls.bottom == 0
        assert window.controls.left == 0
        assert window.controls.right == 0

    def test_set_image_limits_clamps_max(self, window):
        window.controls.set_image_limits(200, 100)
        spins = {sb.objectName(): sb for sb in window.controls.findChildren(QSpinBox)}
        assert spins["spin_top"].maximum() == 99    # img_h - 1
        assert spins["spin_bottom"].maximum() == 99
        assert spins["spin_left"].maximum() == 199  # img_w - 1
        assert spins["spin_right"].maximum() == 199
