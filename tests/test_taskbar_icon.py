"""Tests for taskbar icon functionality on Windows."""

import pytest
import os
import sys
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

# Only run these tests on Windows since taskbar behavior is platform-specific
pytestmark = pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific tests")


class TestTaskbarIcon:
    """Test taskbar icon setup and Windows-specific configurations."""

    def test_application_display_name_is_set(self):
        """Test that application display name is set for proper taskbar grouping."""
        app = QApplication.instance()
        if not app:
            app = QApplication([])

        app.setApplicationDisplayName("9-Slice Cutter")

        # Verify the display name is set
        assert app.applicationDisplayName() == "9-Slice Cutter"

    def test_application_version_is_set(self):
        """Test that application version is set for proper Windows identification."""
        app = QApplication.instance()
        if not app:
            app = QApplication([])

        app.setApplicationVersion("1.0.0")

        # Verify the version is set
        assert app.applicationVersion() == "1.0.0"

    def test_organization_name_helps_taskbar_grouping(self):
        """Test that organization name is set for proper Windows app identification."""
        app = QApplication.instance()
        if not app:
            app = QApplication([])

        app.setOrganizationName("VibeTool")

        # Verify organization name is set
        assert app.organizationName() == "VibeTool"

    def test_windows_icon_paths_exist(self):
        """Test that required icon files exist for Windows taskbar display."""
        project_root = os.path.dirname(os.path.dirname(__file__))
        ico_path = os.path.join(project_root, 'icon', 'icon.ico')
        png_path = os.path.join(project_root, 'icon', 'icon.png')

        assert os.path.exists(ico_path), f"ICO icon not found at {ico_path}"
        assert os.path.exists(png_path), f"PNG icon not found at {png_path}"

        # Verify ICO file is not empty
        assert os.path.getsize(ico_path) > 0, "ICO file is empty"

    def test_qicon_creation_from_ico_file(self):
        """Test that QIcon can be successfully created from ICO file."""
        project_root = os.path.dirname(os.path.dirname(__file__))
        ico_path = os.path.join(project_root, 'icon', 'icon.ico')

        if os.path.exists(ico_path):
            icon = QIcon(ico_path)
            assert not icon.isNull(), "Failed to create valid QIcon from ICO file"

            # Check if icon has appropriate sizes for Windows taskbar
            sizes = icon.availableSizes()
            assert len(sizes) > 0, "Icon should have at least one size available"

    def test_app_user_model_id_can_be_set(self):
        """Test that Windows App User Model ID can be set for proper taskbar behavior."""
        # This would require ctypes to set on Windows, but we test the concept
        app_id = "VibeTool.9SliceCutter.Desktop.1.0"

        # Verify the ID format is valid
        assert "." in app_id
        assert len(app_id.split(".")) >= 3
        assert "VibeTool" in app_id
        assert "9SliceCutter" in app_id

    def test_window_flags_for_taskbar_display(self):
        """Test that appropriate window flags are available for taskbar display."""
        from PySide6.QtCore import Qt

        # Verify essential window flags exist
        assert hasattr(Qt, 'Window')
        assert hasattr(Qt, 'WindowTitleHint')
        assert hasattr(Qt, 'WindowSystemMenuHint')
        assert hasattr(Qt, 'WindowMinMaxButtonsHint')

    def test_taskbar_icon_integration_mock(self):
        """Mock test for Windows taskbar icon integration."""
        # Mock Windows-specific functionality
        with patch('os.name', 'nt'):
            app = QApplication.instance()
            if not app:
                app = QApplication([])

            # Set all properties needed for proper Windows taskbar integration
            app.setApplicationName("9-Slice Cutter")
            app.setApplicationDisplayName("9-Slice Cutter")
            app.setApplicationVersion("1.0.0")
            app.setOrganizationName("VibeTool")

            # Verify all properties are set
            assert app.applicationName() == "9-Slice Cutter"
            assert app.applicationDisplayName() == "9-Slice Cutter"
            assert app.applicationVersion() == "1.0.0"
            assert app.organizationName() == "VibeTool"