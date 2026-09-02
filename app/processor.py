"""
Image processing module — background removal with speed optimizations.

Key optimizations:
  1. Pre-loaded ONNX session (no per-request model loading)
  2. u2net model — full accuracy, keeps subject intact
  3. Image resizing before inference — caps max dimension at 1024px
  4. JPG output with white background
"""

from io import BytesIO

import numpy as np
from PIL import Image
from rembg import remove

# ---------------------------------------------------------------------------
# Session singleton — loaded once, reused for every request
# ---------------------------------------------------------------------------
_session = None


def _get_session():
    """Return the cached rembg session (created once on first call)."""
    global _session
    if _session is None:
        from rembg import new_session
        # u2net: full model, accurate subject detection, keeps foreground intact
        _session = new_session("u2net")
    return _session


def _resize_for_inference(img: Image.Image, max_dim: int = 1024) -> Image.Image:
    """Downscale large images before inference for speed."""
    w, h = img.size
    if max(w, h) <= max_dim:
        return img
    ratio = max_dim / max(w, h)
    new_w, new_h = int(w * ratio), int(h * ratio)
    return img.resize((new_w, new_h), Image.LANCZOS)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def remove_background(
    input_bytes: bytes,
    fill_white: bool = True,
    max_dim: int = 1024,
) -> bytes:
    """
    Remove the background from an image and return as JPG with white background.

    Args:
        input_bytes: Raw image bytes (any format).
        fill_white:  If True, replace transparency with white.
        max_dim:     Max dimension for inference (lower = faster).

    Returns:
        Processed image as JPEG bytes.
    """
    session = _get_session()

    # Open and optionally resize for faster inference
    img = Image.open(BytesIO(input_bytes)).convert("RGB")
    original_size = img.size
    resized = _resize_for_inference(img, max_dim)

    # Convert to numpy for rembg
    img_array = np.ascontiguousarray(np.array(resized, dtype=np.uint8))

    # Run background removal — returns RGBA (subject + transparent bg)
    result = remove(
        img_array,
        session=session,
        only_mask=False,
    )

    # Convert result back to PIL
    result_img = Image.fromarray(result).convert("RGBA")

    # If we resized, upscale the result back to original dimensions
    if result_img.size != original_size:
        result_img = result_img.resize(original_size, Image.LANCZOS)

    if fill_white:
        # Composite subject onto clean white background
        white_bg = Image.new("RGB", original_size, (255, 255, 255))
        # Use the alpha channel from the result as mask
        mask = result_img.split()[3]
        # Paste the RGB portion of the result onto white using the mask
        subject_rgb = result_img.convert("RGB")
        white_bg.paste(subject_rgb, mask=mask)
        output = white_bg
    else:
        output = result_img.convert("RGB")

    # Save as JPEG with high quality
    buf = BytesIO()
    output.save(buf, format="JPEG", quality=95, optimize=True)
    return buf.getvalue()
