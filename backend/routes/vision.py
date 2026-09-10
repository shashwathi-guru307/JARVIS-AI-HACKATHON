# vision.py — vision API endpoints
import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.services.vision_service import (
    run_analysis,
    get_vision_status,
    get_latest_analysis,
)
from backend.utils.config import get_vision_interval

logger   = logging.getLogger(__name__)
router   = APIRouter()

_vision_clients: set[WebSocket] = set()


# ── REST ─────────────────────────────────────────────────────────────────────

@router.get("/vision/status", tags=["Vision"])
def vision_status():
    """Current vision subsystem status."""
    return get_vision_status().model_dump(mode="json")


@router.get("/vision/latest", tags=["Vision"])
def vision_latest():
    """Most recent vision analysis result."""
    result = get_latest_analysis()
    if result is None:
        return {"message": "No vision analysis has run yet. Call POST /vision/analyze first."}
    return result.model_dump(mode="json")


@router.post("/vision/analyze", tags=["Vision"])
def vision_analyze():
    """
    Trigger one synchronous vision analysis cycle.

    The service handles camera availability and demo-mode fallback internally.
    """
    result = run_analysis()
    return result.model_dump(mode="json")


# ── WebSocket ─────────────────────────────────────────────────────────────────

@router.websocket("/ws/vision")
async def vision_stream(websocket: WebSocket):
    """
    Streams vision analysis results every VISION_INTERVAL seconds.
    Mirrors the /ws/telemetry design from Day 2.
    """
    await websocket.accept()
    _vision_clients.add(websocket)
    interval = get_vision_interval()
    logger.info("👁  Vision WebSocket connected  (active: %d)", len(_vision_clients))

    try:
        while True:
            result  = run_analysis()
            payload = json.dumps(result.model_dump(mode="json"))
            await websocket.send_text(payload)
            await asyncio.sleep(interval)
    except WebSocketDisconnect:
        logger.info("👁  Vision WebSocket disconnected")
    except Exception as exc:
        logger.error("Vision WebSocket error: %s", exc)
    finally:
        _vision_clients.discard(websocket)