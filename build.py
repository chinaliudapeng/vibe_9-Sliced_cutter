"""Build script for 9-Slice Cutter standalone executable."""

import subprocess
import sys
import os


def build() -> int:
    """Run PyInstaller to create a standalone windowed executable."""
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "-F",            # Single-file bundle
        "-w",            # Windowed mode (no console window)
        "--name", "9SliceCutter",
        "main.py",
    ]
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
