"""
Test for edge margins (Phase 6) - ensuring canvas has correct border distances.

According to specs/03_ui_layout_interactions.md:
- 图片预览的画布左边缘距离app窗口左侧border距离为10像素
- 图片预览的画布下边缘距离app窗口下方border距离为10像素
"""

import sys
import pytest
from PySide6.QtWidgets import QApplication


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


class TestEdgeMargins:
    """Test edge margin rules for Phase 6."""

    def test_main_layout_has_correct_margins(self, window):
        """Test that the main layout has 10px left and bottom margins."""
        # Get the central widget'''s layout
        central_widget = window.centralWidget()
        layout = central_widget.layout()
        margins = layout.contentsMargins()

        # According to spec: left edge = 10px, bottom edge = 10px
        assert margins.left() == 10, f"Left margin should be 10px, got {margins.left()}px"
        assert margins.bottom() == 10, f"Bottom margin should be 10px, got {margins.bottom()}px"
        # Also verify symmetry for top and right
        assert margins.top() == 10, f"Top margin should be 10px, got {margins.top()}px"
        assert margins.right() == 10, f"Right margin should be 10px, got {margins.right()}px"
