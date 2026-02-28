"""
Phase 5 headless tests: File I/O & full integration.

Covers:
  - dragEnterEvent accepts/rejects URLs by extension
  - _load_image stores source path and enables buttons
  - Overwrite-save confirmation flow (confirmed / cancelled)
  - Save As defaults to source file's directory
"""

import sys
import os
import pytest
from unittest.mock import patch, MagicMock

from PIL import Image
from PySide6.QtWidgets import QApplication, QPushButton, QMessageBox
from PySide6.QtCore import QUrl, QMimeData


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication(sys.argv)
    yield app


@pytest.fixture
def window(qapp):
    from ui.main_window import MainWindow
    win = MainWindow()
    yield win
    win.close()


@pytest.fixture
def loaded_window(qapp, tmp_path):
    """MainWindow with a real 100×80 PNG loaded from a temp path."""
    from ui.main_window import MainWindow
    img = Image.new("RGBA", (100, 80), (200, 150, 100, 255))
    img_path = str(tmp_path / "source.png")
    img.save(img_path)
    win = MainWindow()
    win._load_image(img_path)
    yield win, img_path
    win.close()


# ---------------------------------------------------------------------------
# 1.  dragEnterEvent — extension validation
# ---------------------------------------------------------------------------

class TestDragEnterValidation:
    """Only .png / .jpg / .jpeg URLs should be accepted."""

    def _make_event(self, file_path: str):
        mime = QMimeData()
        mime.setUrls([QUrl.fromLocalFile(file_path)])
        ev = MagicMock()
        ev.mimeData.return_value = mime
        return ev

    def test_accepts_png(self, window, tmp_path):
        path = str(tmp_path / "img.png")
        Image.new("RGBA", (8, 8)).save(path)
        ev = self._make_event(path)
        window.dragEnterEvent(ev)
        ev.acceptProposedAction.assert_called_once()

    def test_accepts_jpg(self, window, tmp_path):
        path = str(tmp_path / "img.jpg")
        Image.new("RGB", (8, 8)).save(path)
        ev = self._make_event(path)
        window.dragEnterEvent(ev)
        ev.acceptProposedAction.assert_called_once()

    def test_accepts_jpeg(self, window, tmp_path):
        path = str(tmp_path / "img.jpeg")
        Image.new("RGB", (8, 8)).save(path)
        ev = self._make_event(path)
        window.dragEnterEvent(ev)
        ev.acceptProposedAction.assert_called_once()

    def test_accepts_uppercase_extension(self, window, tmp_path):
        # Path string with uppercase extension should still be accepted
        path = str(tmp_path / "img.PNG")
        Image.new("RGBA", (8, 8)).save(path)
        ev = self._make_event(path)
        window.dragEnterEvent(ev)
        ev.acceptProposedAction.assert_called_once()

    def test_rejects_txt(self, window, tmp_path):
        path = str(tmp_path / "file.txt")
        (tmp_path / "file.txt").write_text("not an image")
        ev = self._make_event(path)
        window.dragEnterEvent(ev)
        ev.acceptProposedAction.assert_not_called()

    def test_rejects_bmp(self, window, tmp_path):
        # .bmp is not in the accepted list
        path = str(tmp_path / "img.bmp")
        ev = self._make_event(path)
        window.dragEnterEvent(ev)
        ev.acceptProposedAction.assert_not_called()

    def test_rejects_gif(self, window, tmp_path):
        path = str(tmp_path / "img.gif")
        ev = self._make_event(path)
        window.dragEnterEvent(ev)
        ev.acceptProposedAction.assert_not_called()


# ---------------------------------------------------------------------------
# 2.  _load_image behaviour
# ---------------------------------------------------------------------------

class TestLoadImage:

    def test_source_path_stored(self, loaded_window):
        win, img_path = loaded_window
        assert win._source_path == img_path

    def test_source_image_is_set(self, loaded_window):
        win, _ = loaded_window
        assert win._source_image is not None

    def test_image_dimensions_match(self, loaded_window):
        win, _ = loaded_window
        assert win._source_image.size == (100, 80)

    def test_margins_reset_to_zero(self, loaded_window):
        win, _ = loaded_window
        assert win.controls.top == 0
        assert win.controls.bottom == 0
        assert win.controls.left == 0
        assert win.controls.right == 0

    def test_save_as_button_enabled_after_load(self, loaded_window):
        win, _ = loaded_window
        btn = win.findChild(QPushButton, "save_btn")
        assert btn.isEnabled()

    def test_overwrite_button_enabled_after_load(self, loaded_window):
        win, _ = loaded_window
        btn = win.findChild(QPushButton, "overwrite_btn")
        assert btn.isEnabled()


# ---------------------------------------------------------------------------
# 3.  Overwrite-save button state
# ---------------------------------------------------------------------------

class TestOverwriteButtonState:

    def test_overwrite_button_exists(self, window):
        btn = window.findChild(QPushButton, "overwrite_btn")
        assert btn is not None

    def test_overwrite_button_initially_disabled(self, window):
        btn = window.findChild(QPushButton, "overwrite_btn")
        assert not btn.isEnabled()


# ---------------------------------------------------------------------------
# 4.  Overwrite-save flow
# ---------------------------------------------------------------------------

class TestOverwriteSaveFlow:

    def test_confirmed_writes_sliced_image_to_source_path(self, loaded_window):
        """User confirms → sliced output replaces the original file."""
        win, img_path = loaded_window
        win.controls.set_margin_values(10, 10, 10, 10)

        with patch.object(QMessageBox, "warning", return_value=QMessageBox.Yes):
            win._on_overwrite_save_clicked()

        result = Image.open(img_path)
        assert result.size == (10 + 1 + 10, 10 + 1 + 10)  # (21, 21)

    def test_cancelled_does_not_modify_file(self, loaded_window):
        """User cancels → original file is untouched."""
        win, img_path = loaded_window
        original_size = Image.open(img_path).size
        win.controls.set_margin_values(10, 10, 10, 10)

        with patch.object(QMessageBox, "warning", return_value=QMessageBox.No):
            win._on_overwrite_save_clicked()

        result = Image.open(img_path)
        assert result.size == original_size

    def test_does_nothing_when_no_image_loaded(self, window):
        """Should return silently when no image is loaded (no crash)."""
        assert window._source_image is None
        window._on_overwrite_save_clicked()  # must not raise


# ---------------------------------------------------------------------------
# 5.  Save As — defaults to source directory
# ---------------------------------------------------------------------------

class TestSaveAsDirectory:

    def test_dialog_receives_source_directory(self, loaded_window):
        """getSaveFileName is called with the source file's parent directory."""
        win, img_path = loaded_window
        expected_dir = os.path.dirname(img_path)
        captured = {}

        def fake_dialog(parent, caption, directory, filter_str):
            captured["directory"] = directory
            return ("", "")  # simulate cancel

        with patch("PySide6.QtWidgets.QFileDialog.getSaveFileName",
                   side_effect=fake_dialog):
            win._on_save_clicked()

        assert captured.get("directory") == expected_dir

    def test_no_save_when_dialog_cancelled(self, loaded_window, tmp_path):
        """Cancelling the dialog must not write any file."""
        win, img_path = loaded_window
        output_path = str(tmp_path / "output.png")

        with patch("PySide6.QtWidgets.QFileDialog.getSaveFileName",
                   return_value=("", "")):
            win._on_save_clicked()

        assert not os.path.exists(output_path)
