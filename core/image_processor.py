"""
Core 9-slice image processing module (Type B — Engine Standard).

Removes the center cross and retains 1-pixel stretching bands,
producing an output image of size (left + 1 + right, top + 1 + bottom).
"""

from PIL import Image


def slice_image(
    image: Image.Image,
    top: int,
    bottom: int,
    left: int,
    right: int,
) -> Image.Image:
    """Apply the 9-slice Type B algorithm to a PIL Image object.

    Extracts 4 corners, 4 one-pixel edge bands, and 1 center pixel,
    then stitches them into a new image with the center cross removed.

    Args:
        image:  Source PIL Image.
        top:    Top margin in pixels.
        bottom: Bottom margin in pixels.
        left:   Left margin in pixels.
        right:  Right margin in pixels.

    Returns:
        New PIL Image of size (left + 1 + right, top + 1 + bottom).
    """
    # Convert palette mode images to RGBA to avoid palette index issues
    # This ensures proper color handling during cropping and pasting operations
    if image.mode == "P":
        working_image = image.convert("RGBA")
    else:
        working_image = image

    W, H = working_image.size
    new_W = left + 1 + right
    new_H = top + 1 + bottom

    # --- Extract 9 pieces from the source image ---

    # 4 corners
    tl = working_image.crop((0,         0,          left,    top))
    tr = working_image.crop((W - right, 0,          W,       top))
    bl = working_image.crop((0,         H - bottom, left,    H))
    br = working_image.crop((W - right, H - bottom, W,       H))

    # 4 one-pixel edge bands
    # tc: 1px wide column from the left edge of the stretch zone, top-margin height
    tc = working_image.crop((left,      0,          left + 1, top))
    # bc: same column, bottom-margin height
    bc = working_image.crop((left,      H - bottom, left + 1, H))
    # ml: 1px tall row from the top edge of the stretch zone, left-margin width
    ml = working_image.crop((0,         top,        left,     top + 1))
    # mr: same row, right-margin width
    mr = working_image.crop((W - right, top,        W,        top + 1))

    # Center pixel (1×1)
    mc = working_image.crop((left, top, left + 1, top + 1))

    # --- Assemble output image ---
    mode = working_image.mode
    bg = (0, 0, 0, 0) if "A" in mode else (0, 0, 0)
    out = Image.new(mode, (new_W, new_H), bg)

    out.paste(tl, (0,        0))
    out.paste(tc, (left,     0))
    out.paste(tr, (left + 1, 0))

    out.paste(ml, (0,        top))
    out.paste(mc, (left,     top))
    out.paste(mr, (left + 1, top))

    out.paste(bl, (0,        top + 1))
    out.paste(bc, (left,     top + 1))
    out.paste(br, (left + 1, top + 1))

    return out


def process_image(
    source_image_path: str,
    top: int,
    bottom: int,
    left: int,
    right: int,
) -> Image.Image:
    """Load an image from disk and apply the 9-slice algorithm.

    Args:
        source_image_path: Path to the source image (.png / .jpg / .jpeg).
        top:    Top margin in pixels.
        bottom: Bottom margin in pixels.
        left:   Left margin in pixels.
        right:  Right margin in pixels.

    Returns:
        New PIL Image of size (left + 1 + right, top + 1 + bottom).
    """
    image = Image.open(source_image_path)
    return slice_image(image, top, bottom, left, right)
