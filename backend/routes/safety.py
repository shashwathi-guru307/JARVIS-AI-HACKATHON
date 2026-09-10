import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.models.safety_models import EmergencyRequest
from backend.services.safety_service import (
    generate_and_analyze_safety,
    get_latest_safety,
    get_safety_history,
    get_safety_events,
    trigger_emergency,
    reset_emergency,
)

logger = logging.getLogger(__name__)
router = APIRouter()

_safety_clients: set[WebSocket] = set()
_safety_task_started = False
SAFETY_INTERVAL = 3   # seconds


async def _safety_loop() -> None:
    while True:
        try:
            generate_and_analyze_safety()
        except Exception as exc:
            logger.error("Safety loop error: %s", exc)
        await asyncio.sleep(SAFETY_INTERVAL)


@router.on_event("startup")
async def start_safety_loop() -> None:
    global _safety_task_started
    if not _safety_task_started:
        asyncio.create_task(_safety_loop())
        _safety_task_started = True
        logger.info("🛡  Safety monitoring loop started (interval=%ds)", SAFETY_INTERVAL)


# ── REST ──────────────────────────────────────────────────────────────────────

@router.get("/safety/status", tags=["Safety"])
def safety_status():
    s = get_latest_safety()
    if s is None:
        return {"message": "No safety data yet — wait a few seconds."}
    return s.model_dump(mode="json")


@router.get("/safety/history", tags=["Safety"])
def safety_history():
    history = get_safety_history()
    return {
        "device_id": "MACHINE_01",
        "history": [
            {
                "timestamp":   h.timestamp.isoformat(),
                "overall_risk":h.overall_risk,
                "safety_score":h.safety_score,
                "emergency_status": h.emergency_status,
            }
            for h in history
        ],
    }


@router.get("/safety/events", tags=["Safety"])
def safety_events():
    events = get_safety_events()
    return {"events": [e.model_dump(mode="json") for e in events]}


@router.get("/safety/recommendation", tags=["Safety"])
def safety_recommendation():
    s = get_latest_safety()
    if s is None:
        return {"recommendation": "No safety data yet."}
    return {
        "device_id":          s.device_id,
        "overall_risk":       s.overall_risk,
        "recommendation":     s.recommended_action,
        "contributors":       s.contributors,
        "safety_score":       s.safety_score,
    }


@router.post("/safety/emergency", tags=["Safety"])
def trigger_emergency_route(request: EmergencyRequest):
    return trigger_emergency(request.device_id, request.trigger).model_dump()


@router.post("/safety/emergency/reset", tags=["Safety"])
def reset_emergency_route():
    return reset_emergency()


# ── WebSocket ─────────────────────────────────────────────────────────────────

@router.websocket("/ws/safety")
async def safety_stream(websocket: WebSocket):
    await websocket.accept()
    _safety_clients.add(websocket)
    logger.info("🛡  Safety WebSocket connected  (active: %d)", len(_safety_clients))
    try:
        while True:
            status  = generate_and_analyze_safety()
            events  = get_safety_events()
            payload = json.dumps({
                "status": status.model_dump(mode="json"),
                "latest_event": events[0].model_dump(mode="json") if events else None,
            })
            await websocket.send_text(payload)
            await asyncio.sleep(SAFETY_INTERVAL)
    except WebSocketDisconnect:
        logger.info("🛡  Safety WebSocket disconnected")
    except Exception as exc:
        logger.error("Safety WebSocket error: %s", exc)
    finally:
        _safety_clients.discard(websocket)
        