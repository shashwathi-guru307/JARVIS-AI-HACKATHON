# camera.py — camera abstraction; never crashes FastAPI if webcam is absent
import logging
import cv2
import numpy as np

logger = logging.getLogger(__name__)


class CameraService:
    """
    Wraps OpenCV VideoCapture.

    Always call is_available() before read_frame().
    Always call release() when done.
    """

    def __init__(self, device_index: int = 0) -> None:
        self._cap: cv2.VideoCapture | None = None
        self._device_index = device_index
        self._available = False

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def start(self) -> bool:
        """Open the camera. Returns True if successful."""
        try:
            self._cap = cv2.VideoCapture(self._device_index)
            if self._cap.isOpened():
                self._available = True
                logger.info("📷  Camera opened (device %d)", self._device_index)
                return True
            else:
                self._available = False
                logger.warning("📷  Camera device %d not available", self._device_index)
                return False
        except Exception as exc:
            self._available = False
            logger.error("📷  Camera start error: %s", exc)
            return False

    def release(self) -> None:
        """Release the camera resource."""
        if self._cap:
            self._cap.release()
            self._cap = None
        self._available = False
        logger.info("📷  Camera released")

    # ── Frame access ─────────────────────────────────────────────────────────

    def is_available(self) -> bool:
        return self._available and self._cap is not None and self._cap.isOpened()

    def read_frame(self) -> np.ndarray | None:
        """
        Read one frame. Returns the BGR NumPy array or None on failure.
        Automatically marks camera unavailable after repeated failures.
        """
        if not self.is_available():
            return None
        try:
            ret, frame = self._cap.read()
            if ret:
                return frame
            self._available = False
            logger.warning("📷  Frame read failed — camera may have disconnected")
            return None
        except Exception as exc:
            self._available = False
            logger.error("📷  read_frame error: %s", exc)
            return None