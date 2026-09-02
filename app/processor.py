"""
Image processing module — optimized for cloud deployment (Railway/Render).

Uses u2netp model (4.5 MB) which works great on limited RAM/CPU.
Images are resized aggressively to speed up processing.
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
        # u2netp: only 4.5 MB, fast, works on low-memory cloud instances
        _session = new_session("u2netp")
    return _session


def _resize_for_inference(img: Image.Image, max_dim: int = 512) -> Image.Image:
    """Downscale images before inference — critical for cloud speed."""
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
    max_dim: int = 512,
) -> bytes:
    """
    Remove background and return JPG with white background.

    Optimized for cloud: smaller model, aggressive resize.
    """
    session = _get_session()

    # Open and resize for fast inference
    img = Image.open(BytesIO(input_bytes)).convert("RGB")
    original_size = img.size
    resized = _resize_for_inference(img, max_dim)

    # Convert to numpy
    img_array = np.ascontiguousarray(np.array(resized, dtype=np.uint8))

    # Run background removal
    result = remove(
        img_array,
        session=session,
        only_mask=False,
    )

    # Convert back to PIL
    result_img = Image.fromarray(result).convert("RGBA")

    # Upscale mask back to original size
    if result_img.size != original_size:
        result_img = result_img.resize(original_size, Image.LANCZOS)

    if fill_white:
        # Composite onto white background
        white_bg = Image.new("RGB", original_size, (255, 255, 255))
        mask = result_img.split()[3]
        subject_rgb = result_img.convert("RGB")
        white_bg.paste(subject_rgb, mask=mask)
        output = white_bg
    else:
        output = result_img.convert("RGB")

    # Save as JPEG
    buf = BytesIO()
    output.save(buf, format="JPEG", quality=92, optimize=True)
    return buf.getvalue()
