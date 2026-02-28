"""Entry point for the 9-Slice Cutter application."""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from ui.main_window import MainWindow


def main() -> None:
    # Qt6 handles High-DPI natively; no explicit AA_EnableHighDpiScaling needed.
    app = QApplication(sys.argv)

    # Enhanced application identification for better Windows taskbar integration
    app.setApplicationName("9-Slice Cutter")
    app.setApplicationDisplayName("9-Slice Cutter")  # Displayed name in taskbar
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("VibeTool")

    # Windows-specific App User Model ID for proper taskbar grouping and icon display
    if sys.platform == 'win32':
        try:
            import ctypes
            # Set App User Model ID for Windows taskbar recognition
            app_id = "VibeTool.9SliceCutter.Desktop.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        except (ImportError, AttributeError, OSError):
            # Silently continue if Windows API is not available
            pass

    # Set application icon for taskbar, system tray, and default window icon
    icon_paths = [
        os.path.join(os.path.dirname(__file__), 'icon', 'icon.ico'),
        os.path.join(os.path.dirname(__file__), 'icon', 'icon.png'),
    ]

    for icon_path in icon_paths:
        if os.path.exists(icon_path):
            try:
                icon = QIcon(icon_path)
                if not icon.isNull():
                    app.setWindowIcon(icon)
                    break
            except Exception:
                continue

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
