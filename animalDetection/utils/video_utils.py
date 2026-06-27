"""
Video utility functions for opening video sources and reading frames.
"""

try:
    import cv2
except ImportError:
    raise ImportError(
        "OpenCV not found. Install with: pip install opencv-python-headless"
    )

import os


SUPPORTED_VIDEO_FORMATS = (
    ("Video Files", "*.mp4 *.avi *.mov *.mkv"),
    ("MP4", "*.mp4"),
    ("AVI", "*.avi"),
    ("MOV", "*.mov"),
    ("MKV", "*.mkv"),
    ("All Files", "*.*"),
)


def open_video_file(file_path: str) -> cv2.VideoCapture:
    """
    Open a video file and return a VideoCapture object.

    Args:
        file_path: absolute path to video file

    Returns:
        cv2.VideoCapture object

    Raises:
        FileNotFoundError: if file does not exist
        RuntimeError: if video cannot be opened
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Video file not found: {file_path}")

    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video file: {file_path}")
    return cap


def open_webcam(index: int = 0) -> cv2.VideoCapture:
    """
    Open a webcam at the given device index.

    Args:
        index: webcam device index (default 0)

    Returns:
        cv2.VideoCapture object

    Raises:
        RuntimeError: if webcam cannot be opened
    """
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        raise RuntimeError(
            f"Could not open webcam at index {index}. "
            "Check that a camera is connected and not in use."
        )
    return cap


def get_video_fps(cap: cv2.VideoCapture) -> float:
    """Get the FPS of a VideoCapture, returning 30.0 as fallback."""
    fps = cap.get(cv2.CAP_PROP_FPS)
    return fps if fps > 0 else 30.0
