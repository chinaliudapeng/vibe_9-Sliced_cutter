"""
Tests for core/image_processor.py — Phase 2 (TDD).

All tests are pure-logic / headless; no GUI or disk I/O except where
explicitly testing the file-loading helper.
"""

import pytest
from PIL import Image

from core.image_processor import process_image, slice_image


# ---------------------------------------------------------------------------
# Output-size tests (the primary spec requirement)
# ---------------------------------------------------------------------------

class TestOutputSize:
    """Output dimensions must always equal (left+1+right, top+1+bottom)."""

    def test_symmetric_margins(self):
        img = Image.new("RGBA", (100, 80), (255, 0, 0, 255))
        result = slice_image(img, top=8, bottom=8, left=10, right=10)
        assert result.size == (10 + 1 + 10, 8 + 1 + 8)
        assert result.size == (21, 17)

    def test_asymmetric_margins(self):
        img = Image.new("RGBA", (200, 150), (0, 255, 0, 255))
        top, bottom, left, right = 20, 30, 15, 25
        result = slice_image(img, top=top, bottom=bottom, left=left, right=right)
        assert result.size == (left + 1 + right, top + 1 + bottom)
        assert result.size == (41, 51)

    def test_minimal_margins(self):
        img = Image.new("RGBA", (10, 10), (0, 0, 255, 255))
        result = slice_image(img, top=1, bottom=1, left=1, right=1)
        assert result.size == (3, 3)

    @pytest.mark.parametrize("W,H,top,bottom,left,right", [
        (50,  40,  5, 10,  7,  8),
        (100, 100, 20, 20, 20, 20),
        (200, 150, 30, 25, 40, 35),
        (64,  64,  8, 16, 12, 12),
    ])
    def test_formula_parametric(self, W, H, top, bottom, left, right):
        img = Image.new("RGBA", (W, H), (128, 128, 128, 255))
        result = slice_image(img, top=top, bottom=bottom, left=left, right=right)
        assert result.size == (left + 1 + right, top + 1 + bottom), (
            f"margins=({top},{bottom},{left},{right}): "
            f"expected ({left+1+right},{top+1+bottom}), got {result.size}"
        )


# ---------------------------------------------------------------------------
# Pixel-content tests
# ---------------------------------------------------------------------------

class TestCornerPixels:
    """Corner pixels in the output must match the source corners."""

    def _make_colored_image(self, W, H, top, bottom, left, right):
        """Create an image with distinct solid colors in each of the 9 regions."""
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        colors = {
            "tl": (255, 0,   0,   255),
            "tr": (0,   255, 0,   255),
            "bl": (0,   0,   255, 255),
            "br": (255, 255, 0,   255),
            "cx": (128, 128, 128, 255),  # center cross region
        }
        # TL corner
        for y in range(top):
            for x in range(left):
                img.putpixel((x, y), colors["tl"])
        # TR corner
        for y in range(top):
            for x in range(W - right, W):
                img.putpixel((x, y), colors["tr"])
        # BL corner
        for y in range(H - bottom, H):
            for x in range(left):
                img.putpixel((x, y), colors["bl"])
        # BR corner
        for y in range(H - bottom, H):
            for x in range(W - right, W):
                img.putpixel((x, y), colors["br"])
        return img, colors

    def test_top_left_corner(self):
        W, H, top, bottom, left, right = 100, 80, 10, 10, 15, 15
        img, colors = self._make_colored_image(W, H, top, bottom, left, right)
        result = slice_image(img, top=top, bottom=bottom, left=left, right=right)
        assert result.getpixel((0, 0)) == colors["tl"]
        assert result.getpixel((left - 1, top - 1)) == colors["tl"]

    def test_top_right_corner(self):
        W, H, top, bottom, left, right = 100, 80, 10, 10, 15, 15
        img, colors = self._make_colored_image(W, H, top, bottom, left, right)
        result = slice_image(img, top=top, bottom=bottom, left=left, right=right)
        new_W = left + 1 + right
        assert result.getpixel((left + 1, 0)) == colors["tr"]
        assert result.getpixel((new_W - 1, top - 1)) == colors["tr"]

    def test_bottom_left_corner(self):
        W, H, top, bottom, left, right = 100, 80, 10, 10, 15, 15
        img, colors = self._make_colored_image(W, H, top, bottom, left, right)
        result = slice_image(img, top=top, bottom=bottom, left=left, right=right)
        new_H = top + 1 + bottom
        assert result.getpixel((0, top + 1)) == colors["bl"]
        assert result.getpixel((left - 1, new_H - 1)) == colors["bl"]

    def test_bottom_right_corner(self):
        W, H, top, bottom, left, right = 100, 80, 10, 10, 15, 15
        img, colors = self._make_colored_image(W, H, top, bottom, left, right)
        result = slice_image(img, top=top, bottom=bottom, left=left, right=right)
        new_W = left + 1 + right
        new_H = top + 1 + bottom
        assert result.getpixel((left + 1, top + 1)) == colors["br"]
        assert result.getpixel((new_W - 1, new_H - 1)) == colors["br"]


# ---------------------------------------------------------------------------
# Image-mode tests
# ---------------------------------------------------------------------------

class TestImageMode:
    def test_rgba_mode_preserved(self):
        img = Image.new("RGBA", (100, 80), (0, 0, 0, 0))
        result = slice_image(img, top=10, bottom=10, left=10, right=10)
        assert result.mode == "RGBA"

    def test_rgb_mode_preserved(self):
        img = Image.new("RGB", (100, 80), (255, 255, 255))
        result = slice_image(img, top=10, bottom=10, left=10, right=10)
        assert result.mode == "RGB"


# ---------------------------------------------------------------------------
# File-loading helper
# ---------------------------------------------------------------------------

class TestProcessImageFile:
    def test_loads_file_and_returns_correct_size(self, tmp_path):
        img = Image.new("RGBA", (100, 80), (255, 128, 0, 255))
        filepath = str(tmp_path / "test.png")
        img.save(filepath)

        result = process_image(filepath, top=10, bottom=10, left=10, right=10)
        assert result.size == (21, 21)

    def test_jpg_file_supported(self, tmp_path):
        img = Image.new("RGB", (120, 100), (200, 100, 50))
        filepath = str(tmp_path / "test.jpg")
        img.save(filepath)

        result = process_image(filepath, top=12, bottom=12, left=15, right=15)
        assert result.size == (15 + 1 + 15, 12 + 1 + 12)
        assert result.size == (31, 25)
