#!/usr/bin/env python3
"""
Convert PNG icon to ICO format for Windows taskbar icon support.
This script creates a multi-resolution ICO file from the source PNG.
"""

from PIL import Image
import os

def convert_png_to_ico():
    """Convert icon/icon.png to icon/icon.ico with multiple sizes."""
    png_path = "icon/icon.png"
    ico_path = "icon/icon.ico"

    if not os.path.exists(png_path):
        print(f"ERROR: {png_path} not found!")
        return False

    try:
        # Load the PNG image
        img = Image.open(png_path)

        # Convert to RGBA if not already (needed for ICO)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Create multiple sizes for the ICO file
        # Windows taskbar typically uses 16x16, 32x32, 48x48, 256x256
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

        # Resize to all required sizes
        icons = []
        for size in sizes:
            resized = img.resize(size, Image.Resampling.LANCZOS)
            icons.append(resized)

        # Save as ICO with multiple sizes
        icons[0].save(ico_path, format='ICO', sizes=[icon.size for icon in icons])

        print(f"Successfully converted {png_path} to {ico_path}")
        print(f"   Created {len(sizes)} icon sizes: {', '.join(f'{w}x{h}' for w, h in sizes)}")
        return True

    except Exception as e:
        print(f"ERROR converting icon: {e}")
        return False

if __name__ == "__main__":
    convert_png_to_ico()