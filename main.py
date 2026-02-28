"""Entry point for the 9-Slice Cutter application."""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from ui.main_window import MainWindow


def main() -> None:
    # Qt6 handles High-DPI natively; no explicit AA_EnableHighDpiScaling needed.
    app = QApplication(sys.argv)
    app.setApplicationName("9-Slice Cutter")
    app.setOrganizationName("VibeTool")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
