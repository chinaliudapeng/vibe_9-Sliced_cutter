# Core Module: Image Processing (Pillow)

## 1. Responsibilities
Handle all pixel-level manipulations using the `Pillow` library. This module should not contain any GUI code.

## 2. Input Parameters
- `source_image_path` (str): Path to the original image.
- `top` (int), `bottom` (int), `left` (int), `right` (int): Margin values in pixels.

## 3. The "Center Cross" Removal Algorithm (Type B - Engine Standard)
To ensure the output image scales correctly in engines without corner distortion, we do NOT discard the entire center. We must retain a 1-pixel stretching band.


**Step-by-step logic:**
1. Read the original image size `(W, H)`.
2. Extract the 4 corners:
   - Top-Left: `(0, 0)` to `(left, top)`
   - Top-Right: `(W-right, 0)` to `(W, top)`
   - Bottom-Left: `(0, H-bottom)` to `(left, H)`
   - Bottom-Right: `(W-right, H-bottom)` to `(W, H)`
3. Extract the 1-pixel stretching bands (taking the middle pixel of the respective edges):
   - Top band (1px high): `(left, top-1)` to `(W-right, top)`
   - Bottom band (1px high): `(left, H-bottom)` to `(W-right, H-bottom+1)`
   - Left band (1px wide): `(left-1, top)` to `(left, H-bottom)`
   - Right band (1px wide): `(W-right, top)` to `(W-right+1, H-bottom)`
   - Center pixel (1x1): The exact center pixel of the original stretch zone.
4. Calculate new image size: `New_W = left + 1 + right`, `New_H = top + 1 + bottom`.
5. Create a new transparent image with `(New_W, New_H)` and paste the 9 extracted pieces into their exact relative positions.
6. Return the `Image` object or save it directly.