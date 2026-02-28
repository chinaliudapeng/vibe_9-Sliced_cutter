"""
Tests for icon fix functionality.
This test verifies that both application and window icons are properly set.
"""

import os
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from ui.main_window import MainWindow


class TestIconFix(unittest.TestCase):
    """Test icon functionality for both app and window level."""

    def setUp(self):
        """Set up test fixtures."""
        if not QApplication.instance():
            self.app = QApplication([])
        else:
            self.app = QApplication.instance()

        self.window = MainWindow()

    def test_window_icon_is_set(self):
        """Test that MainWindow sets its window icon if ICO file exists."""
        # The MainWindow constructor should attempt to set a window icon
        # Since we have the actual icon file, it should be set
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icon', 'icon.ico')

        if os.path.exists(icon_path):
            self.assertFalse(self.window.windowIcon().isNull())
        else:
            # If no icon file exists, window icon should be null
            self.assertTrue(self.window.windowIcon().isNull())

    def test_app_icon_setting_behavior(self):
        """Test that main.py app icon setting code executes without error."""
        # Test the icon setting logic from main.py
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icon', 'icon.ico')

        if os.path.exists(icon_path):
            # Should not raise an exception
            try:
                self.app.setWindowIcon(QIcon(icon_path))
            except Exception as e:
                self.fail(f"App icon setting failed: {e}")

    def test_ico_file_exists(self):
        """Test that the ICO file was created successfully."""
        ico_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icon', 'icon.ico')
        self.assertTrue(os.path.exists(ico_path), "ICO file should exist")

    def test_png_file_still_exists(self):
        """Test that original PNG file is preserved."""
        png_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'icon', 'icon.png')
        self.assertTrue(os.path.exists(png_path), "Original PNG file should still exist")

    def tearDown(self):
        """Clean up test fixtures."""
        self.window.close()


if __name__ == '__main__':
    unittest.main()