# vision_service.py — orchestrates camera, processing, and analysis
import logging
import random
from datetime import datetime, timezone

from backend.vision.camera import CameraService
from backend.vision.processor import MotionDetector, resize_frame, frame_to_base64
from backend.vision.sample_data.generate_sample import make_demo_frame
from backend.models.vision_models import VisionAnalysis, VisionStatus
from backend.utils.config import get_vision_enabled, get_vision_mode, get_vision_interval

logger = logging.getLogger(__name__)

# ── Module-level singletons ───────────────────────────────────────────────────
_camera   = CameraService()
_detector = MotionDetector()

# In-memory state
_latest_analysis: VisionAnalysis | None = None
_processing = False


# ── Helpers ───────────────────────────────────────────────────────────────────

def _analyse_local(frame) -> VisionAnalysis:
    """Run OpenCV motion detection on a real or demo frame."""
    result = _detector.detect(frame)
    detected   = result["detected"]
    confidence = result["confidence"]

    if detected and confidence >= 0.6:
        risk_level = "CRITICAL"
        event      = "motion_detected"
        summary    = "Significant motion detected in the monitored area."
        action     = "Inspect the area immediately."
    elif detected:
        risk_level = "WARNING"
        event      = "motion_detected"
        summary    = "Possible motion detected — confidence is moderate."
        action     = "Monitor the area for continued activity."
    else:
        risk_level = "NORMAL"
        event      = "scene_normal"
        summary    = "No significant motion detected. Scene appears stable."
        action     = "Continue monitoring."

    return VisionAnalysis(
        timestamp=datetime.now(timezone.utc),
        detected=detected,
        event=event,
        objects=[],
        risk_level=risk_level,
        summary=summary,
        recommended_action=action,
        confidence=confidence,
    )


def _analyse_demo() -> VisionAnalysis:
    """
    Return a synthetic result for DEMO mode (no camera, no AI needed).
    Occasionally simulates a motion event to make the HUD feel alive.
    """
    simulated_motion = random.random() < 0.15   # 15 % chance

    if simulated_motion:
        confidence = round(random.uniform(0.55, 0.92), 2)
        return VisionAnalysis(
            timestamp=datetime.now(timezone.utc),
            detected=True,
            event="motion_detected",
            objects=[],
            risk_level="WARNING" if confidence < 0.75 else "CRITICAL",
            summary="[DEMO] Simulated motion event detected.",
            recommended_action="Inspect the monitored area.",
            confidence=confidence,
        )
    return VisionAnalysis(
        timestamp=datetime.now(timezone.utc),
        detected=False,
        event="scene_normal",
        objects=[],
        risk_level="NORMAL",
        summary="[DEMO] Scene appears stable.",
        recommended_action="Continue monitoring.",
        confidence=round(random.uniform(0.80, 0.99), 2),
    )


# ── Public API ────────────────────────────────────────────────────────────────

def get_camera_status() -> str:
    if not get_vision_enabled():
        return "DISABLED"
    mode = get_vision_mode()
    if mode == "demo":
        return "DEMO"
    return "CONNECTED" if _camera.is_available() else "DISCONNECTED"


def get_vision_status() -> VisionStatus:
    return VisionStatus(
        camera=get_camera_status(),
        vision_mode=get_vision_mode(),
        processing=_processing,
        last_analysis=_latest_analysis.timestamp if _latest_analysis else None,
    )


def get_latest_analysis() -> VisionAnalysis | None:
    return _latest_analysis


def run_analysis() -> VisionAnalysis:
    """
    Main entry point — called by the API route or a periodic task.

    Priority:
      1. DEMO mode  → synthetic result, no hardware needed
      2. LOCAL mode → try camera; fall back to demo frame if unavailable
      3. On any error → fall back to demo
    """
    global _latest_analysis, _processing
    mode = get_vision_mode()

    _processing = True
    try:
        if not get_vision_enabled() or mode == "demo":
            result = _analyse_demo()
        else:
            # Try to open camera if not already open
            if not _camera.is_available():
                opened = _camera.start()
                if not opened:
                    logger.warning("📷  Camera unavailable — switching to DEMO mode for this cycle")
                    result = _analyse_demo()
                    _latest_analysis = result
                    return result

            frame = _camera.read_frame()
            if frame is None:
                logger.warning("📷  Frame read failed — using demo frame")
                frame = make_demo_frame()

            frame = resize_frame(frame)
            result = _analyse_local(frame)

        if result.risk_level != "NORMAL":
            logger.warning("👁  Vision: %s  confidence=%.2f", result.event, result.confidence)
        else:
            logger.info("👁  Vision: NORMAL  confidence=%.2f", result.confidence)

        _latest_analysis = result
        return result

    except Exception as exc:
        logger.error("Vision analysis error: %s", exc)
        fallback = _analyse_demo()
        _latest_analysis = fallback
        return fallback
    finally:
        _processing = False


def shutdown() -> None:
    """Release camera on application shutdown."""
    _camera.release()