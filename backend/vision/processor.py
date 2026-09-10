# processor.py — OpenCV frame preprocessing and local motion detection
import logging
import base64
import cv2
import numpy as np
from PIL import Image
import io

logger = logging.getLogger(__name__)

# Maximum dimension (width or height) after resizing — keeps analysis fast
MAX_DIMENSION = 640

# Motion detection: minimum contour area to count as "motion"
MOTION_MIN_AREA = 1500


def resize_frame(frame: np.ndarray) -> np.ndarray:
    """Resize a frame so neither dimension exceeds MAX_DIMENSION."""
    h, w = frame.shape[:2]
    scale = min(MAX_DIMENSION / w, MAX_DIMENSION / h, 1.0)
    if scale < 1.0:
        new_w = int(w * scale)
        new_h = int(h * scale)
        frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return frame


def frame_to_jpeg_bytes(frame: np.ndarray, quality: int = 70) -> bytes:
    """Encode a BGR frame to JPEG bytes."""
    _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return buf.tobytes()


def frame_to_base64(frame: np.ndarray) -> str:
    """Return a base64-encoded JPEG string (for API transport if needed)."""
    return base64.b64encode(frame_to_jpeg_bytes(frame)).decode()


class MotionDetector:
    """
    Simple background-subtraction motion detector.

    Not ML — just OpenCV MOG2 background subtractor.
    Works entirely offline and is fast on a laptop.
    """

    def __init__(self) -> None:
        self._subtractor = cv2.createBackgroundSubtractorMOG2(
            history=100, varThreshold=40, detectShadows=False
        )

    def detect(self, frame: np.ndarray) -> dict:
        """
        Run motion detection on one frame.

        Returns a dict with:
          detected      bool
          motion_area   float  (fraction of frame that moved, 0–1)
          confidence    float
        """
        small = resize_frame(frame)
        gray  = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        mask  = self._subtractor.apply(gray)

        # Remove noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask   = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        significant = [c for c in contours if cv2.contourArea(c) > MOTION_MIN_AREA]

        total_pixels  = small.shape[0] * small.shape[1]
        motion_area   = sum(cv2.contourArea(c) for c in significant) / total_pixels
        detected      = len(significant) > 0
        confidence    = min(round(motion_area * 10, 2), 1.0)  # simple normalisation

        return {
            "detected":    detected,
            "motion_area": round(motion_area, 4),
            "confidence":  max(confidence, 0.0),
        }