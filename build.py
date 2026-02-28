"""Build script for 9-Slice Cutter standalone executable."""

import subprocess
import sys
import os


def build() -> int:
    """Run PyInstaller to create a standalone windowed executable."""
    # Check for icon file
    icon_path = os.path.join(os.path.dirname(__file__), 'icon', 'icon.ico')
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "-F",            # Single-file bundle
        "-w",            # Windowed mode (no console window)
        "--name", "9SliceCutter",
    ]

    # Add icon if it exists
    if os.path.exists(icon_path):
        cmd.extend(["--icon", icon_path])

    cmd.append("main.py")
    print("Building 9SliceCutter executable...")
    print(" ".join(cmd))
    result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
    if result.returncode == 0:
        print("\nBuild complete! Output: dist/9SliceCutter.exe")
    else:
        print("\nBuild FAILED.")
    return result.returncode


if __name__ == "__main__":
    sys.exit(build())
