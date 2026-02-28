"""
Test for window icon functionality (Phase 12).

This test verifies that the main window correctly sets its window icon
(the small icon shown in the window's title bar/left corner).
"""

import os
import sys
import pytest
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ui.main_window import MainWindow


class TestWindowIcon:
    """Test window icon functionality."""

    @pytest.fixture(autouse=True)
    def setup_qt_app(self):
        """Ensure we have a QApplication instance for tests."""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()
        yield
        # Clean up if we created the app
        if hasattr(self, 'app') and self.app:
            self.app.quit()

    def test_window_icon_file_exists(self):
        """Test that the icon file exists in the expected location."""
        project_root = os.path.dirname(os.path.dirname(__file__))
        icon_path = os.path.join(project_root, 'icon', 'icon.ico')
        assert os.path.exists(icon_path), f"Icon file not found at {icon_path}"

    def test_window_has_icon_set(self):
        """Test that MainWindow sets a window icon."""
        window = MainWindow()

        # Check that window icon is set (not null/empty)
        icon = window.windowIcon()
        assert not icon.isNull(), "Window icon should not be null"

        window.close()

    def test_icon_path_resolution(self):
        """Test that the icon path is correctly resolved."""
        window = MainWindow()

        # Manually check the path construction logic
        project_root = os.path.dirname(os.path.dirname(__file__))
        expected_icon_path = os.path.join(project_root, 'icon', 'icon.ico')

        assert os.path.exists(expected_icon_path), f"Expected icon path {expected_icon_path} does not exist"

        # Verify the icon can be loaded
        icon = QIcon(expected_icon_path)
        assert not icon.isNull(), "Icon should load successfully from the expected path"

        window.close()

    def test_window_icon_is_properly_configured(self):
        """Test that window icon is configured correctly at window creation."""
        # Test that the window icon path logic works correctly
        window = MainWindow()

        # Get the expected icon path using the same logic as MainWindow
        import os
        project_root = os.path.dirname(os.path.dirname(__file__))
        expected_icon_path = os.path.join(project_root, 'icon', 'icon.ico')

        # Verify the path exists and icon is set
        assert os.path.exists(expected_icon_path), f"Icon file should exist at {expected_icon_path}"

        # Verify window icon is not null
        icon = window.windowIcon()
        assert not icon.isNull(), "Window icon should be set and not null"

        window.close()

    def test_icon_display_properties(self):
        """Test icon properties for display."""
        project_root = os.path.dirname(os.path.dirname(__file__))
        icon_path = os.path.join(project_root, 'icon', 'icon.ico')

        if os.path.exists(icon_path):
            icon = QIcon(icon_path)

            # Test that icon has available sizes
            sizes = icon.availableSizes()
            assert len(sizes) > 0, "Icon should have at least one available size"

            # Test that icon can render at common window icon sizes
            common_sizes = [(16, 16), (32, 32), (48, 48)]
            for width, height in common_sizes:
                pixmap = icon.pixmap(width, height)
                assert not pixmap.isNull(), f"Icon should render at size {width}x{height}"

    def test_window_title_and_icon_together(self):
        """Test that both window title and icon are set correctly."""
        window = MainWindow()

        # Check window title
        assert window.windowTitle() == "9-Slice Cutter"

        # Check window icon is set
        icon = window.windowIcon()
        assert not icon.isNull(), "Window should have an icon"

        window.close()

    def test_icon_setup_method_exists(self):
        """Test that the _setup_window_icon method exists and works."""
        window = MainWindow()

        # Check that the setup method exists
        assert hasattr(window, '_setup_window_icon'), "MainWindow should have _setup_window_icon method"

        # Call the method manually (should not raise an exception)
        window._setup_window_icon()

        # Check that icon is still set after calling the method
        icon = window.windowIcon()
        assert not icon.isNull(), "Window icon should be set after calling _setup_window_icon"

        window.close()

    def test_icon_fallback_when_file_missing(self):
        """Test that fallback icon works when icon files are missing."""
        # Temporarily rename the icon directory to simulate missing icons
        project_root = os.path.dirname(os.path.dirname(__file__))
        icon_dir = os.path.join(project_root, 'icon')
        temp_name = icon_dir + '_temp_renamed'

        # Skip this test if we can't rename (permissions, etc.)
        try:
            if os.path.exists(icon_dir):
                os.rename(icon_dir, temp_name)

            # Create window without icon files
            window = MainWindow()

            # Should have fallback icon
            icon = window.windowIcon()
            assert not icon.isNull(), "Should have fallback icon when files are missing"

            window.close()

        finally:
            # Restore original directory
            if os.path.exists(temp_name):
                os.rename(temp_name, icon_dir)

    def test_multiple_icon_formats_support(self):
        """Test that both ICO and PNG icon formats are supported."""
        project_root = os.path.dirname(os.path.dirname(__file__))
        ico_path = os.path.join(project_root, 'icon', 'icon.ico')
        png_path = os.path.join(project_root, 'icon', 'icon.png')

        # Test ICO format if it exists
        if os.path.exists(ico_path):
            ico_icon = QIcon(ico_path)
            assert not ico_icon.isNull(), "ICO icon should load successfully"

        # Test PNG format if it exists
        if os.path.exists(png_path):
            png_icon = QIcon(png_path)
            assert not png_icon.isNull(), "PNG icon should load successfully"

        # At least one format should exist
        assert os.path.exists(ico_path) or os.path.exists(png_path), "At least one icon format should exist"

if __name__ == "__main__":
    pytest.main([__file__])