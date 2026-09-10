# generate_sample.py — produces a synthetic BGR frame for demo mode
import numpy as np
import cv2


def make_demo_frame() -> np.ndarray:
    """
    Return a 480×640 BGR image that simulates a machine room still.
    Used when no real camera is available (DEMO mode).
    """
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    # Dark grey background
    frame[:] = (30, 30, 30)
    # Add some rectangles to simulate machinery outlines
    cv2.rectangle(frame, (80, 100), (280, 380), (60, 60, 60), -1)
    cv2.rectangle(frame, (320, 150), (560, 350), (50, 50, 55), -1)
    cv2.putText(frame, "DEMO FRAME — NO CAMERA", (60, 460),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)
    return frame