"""
Image utility functions for loading, resizing, and converting images.
"""

try:
    from PIL import Image, ImageTk
except ImportError:
    raise ImportError(
        "Pillow not found. Install with: pip install Pillow"
    )

try:
    import cv2
except ImportError:
    raise ImportError(
        "OpenCV not found. Install with: pip install opencv-python-headless"
    )

import numpy as np
import os


SUPPORTED_IMAGE_FORMATS = (
    ("Image Files", "*.jpg *.jpeg *.png *.bmp *.webp"),
    ("JPEG", "*.jpg *.jpeg"),
    ("PNG", "*.png"),
    ("BMP", "*.bmp"),
    ("WebP", "*.webp"),
    ("All Files", "*.*"),
)


def load_image_cv2(file_path: str) -> np.ndarray:
    """
    Load an image from disk using OpenCV (returns BGR numpy array).

    Args:
        file_path: absolute path to the image file

    Returns:
        BGR numpy array

    Raises:
        FileNotFoundError: if file does not exist
        ValueError: if file cannot be decoded as an image
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")

    img = cv2.imread(file_path)
    if img is None:
        raise ValueError(f"Could not decode image: {file_path}")
    return img


def bgr_to_pil(bgr_frame: np.ndarray) -> Image.Image:
    """Convert a BGR OpenCV frame to a PIL Image (RGB)."""
    rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


def resize_to_fit(image: Image.Image, max_width: int, max_height: int) -> Image.Image:
    """
    Resize a PIL image to fit within max dimensions, preserving aspect ratio.
    """
    w, h = image.size
    if w == 0 or h == 0:
        return image

    scale = min(max_width / w, max_height / h, 1.0)
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))
    return image.resize((new_w, new_h), Image.LANCZOS)


def pil_to_photoimage(image: Image.Image) -> ImageTk.PhotoImage:
    """Convert a PIL Image to a tkinter-compatible PhotoImage."""
    return ImageTk.PhotoImage(image)
