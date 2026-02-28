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
    app.setApplicationName("9-Slice Cutter")
    app.setOrganizationName("VibeTool")

    # Set application icon for taskbar and system tray
    icon_path = os.path.join(os.path.dirname(__file__), 'icon', 'icon.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
