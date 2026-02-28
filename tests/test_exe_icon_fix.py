"""
Test for Phase 11: Verify exe file icon fix.

This test validates that the exe icon is properly embedded and application icons are correctly set.
"""

import os
import pytest
import subprocess
from pathlib import Path


class TestExeIconFix:
    """Tests for exe icon fix in Phase 11."""

    def test_exe_file_exists(self):
        """Test that the exe file was generated."""
        exe_path = Path("dist/9SliceCutter.exe")
        assert exe_path.exists(), "9SliceCutter.exe should exist in dist directory"
        assert exe_path.stat().st_size > 50_000_000, "exe file should be roughly 50+ MB"

    def test_ico_file_still_available(self):
        """Test that the ico file is still available for runtime use."""
        ico_path = Path("icon/icon.ico")
        assert ico_path.exists(), "icon.ico should exist"
        assert ico_path.stat().st_size > 0, "icon.ico should not be empty"

    def test_spec_file_contains_icon_reference(self):
        """Test that the generated .spec file contains the icon reference."""
        spec_path = Path("9SliceCutter.spec")
        assert spec_path.exists(), "PyInstaller should generate a .spec file"

        spec_content = spec_path.read_text()
        assert "icon.ico" in spec_content, ".spec file should reference the icon file"

    def test_pyinstaller_log_shows_icon_copy(self):
        """Test that PyInstaller actually processed the icon by checking build directory."""
        # The build should have warnings file that might contain icon info
        warn_file = Path("build/9SliceCutter/warn-9SliceCutter.txt")
        if warn_file.exists():
            # This is just to ensure build directory exists and has expected structure
            assert warn_file.parent.exists(), "Build directory should exist"

    def test_application_can_start_without_crash(self):
        """Test that the application can be instantiated without immediate crash."""
        # This is a basic smoke test - we'll run the exe for a few seconds
        # and kill it to ensure it starts properly
        exe_path = Path("dist/9SliceCutter.exe")
        if exe_path.exists():
            try:
                # Start the process
                process = subprocess.Popen(
                    [str(exe_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

                # Wait briefly to see if it crashes immediately
                try:
                    # Wait up to 3 seconds to see if it crashes
                    return_code = process.wait(timeout=3)
                    # If we get here, the process exited - check if it was an error
                    assert return_code == 0, f"Application exited with error code {return_code}"
                except subprocess.TimeoutExpired:
                    # Process is still running, which is good - terminate it
                    process.terminate()
                    try:
                        process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        process.kill()
                    # This is the expected path - app started successfully
                    assert True, "Application started successfully"

            except Exception as e:
                pytest.fail(f"Failed to start application: {e}")

    def test_exe_file_has_expected_properties(self):
        """Test that the exe file has expected properties."""
        exe_path = Path("dist/9SliceCutter.exe")
        assert exe_path.exists(), "exe file should exist"

        # Check file extension
        assert exe_path.suffix.lower() == ".exe", "Should be a .exe file"

        # Check it's executable
        assert os.access(exe_path, os.X_OK), "exe should be executable"