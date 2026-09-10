import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.services.energy_service import (
    generate_and_analyze_energy,
    get_latest_metrics,
    get_latest_optimization,
    get_energy_history,
    get_energy_forecast,
    get_load_schedule,
)
from backend.utils.config import get_prediction_interval

logger = logging.getLogger(__name__)
router = APIRouter()

_energy_clients: set[WebSocket] = set()
_energy_task_started = False

ENERGY_INTERVAL = 3   # seconds between energy readings


async def _energy_loop() -> None:
    while True:
        try:
            generate_and_analyze_energy()
        except Exception as exc:
            logger.error("Energy loop error: %s", exc)
        await asyncio.sleep(ENERGY_INTERVAL)


@router.on_event("startup")
async def start_energy_loop() -> None:
    global _energy_task_started
    if not _energy_task_started:
        asyncio.create_task(_energy_loop())
        _energy_task_started = True
        logger.info("⚡  Energy intelligence loop started (interval=%ds)", ENERGY_INTERVAL)


# ── REST ──────────────────────────────────────────────────────────────────────

@router.get("/energy/status", tags=["Energy"])
def energy_status():
    """Current energy metrics."""
    m = get_latest_metrics()
    if m is None:
        return {"message": "No energy data yet — wait a few seconds."}
    return m.model_dump(mode="json")


@router.get("/energy/history", tags=["Energy"])
def energy_history():
    """Recent energy history (last 500 readings)."""
    history = get_energy_history()
    return {"device_id": "MACHINE_01", "history": [h.model_dump(mode="json") for h in history]}


@router.get("/energy/forecast", tags=["Energy"])
def energy_forecast():
    """Short-term energy demand forecast."""
    forecast = get_energy_forecast()
    if forecast is None:
        return {"message": "Not enough data for a forecast yet. Please wait."}
    return forecast.model_dump(mode="json")


@router.get("/energy/recommendation", tags=["Energy"])
def energy_recommendation():
    """Latest energy optimization recommendation."""
    opt = get_latest_optimization()
    if opt is None:
        return {"message": "No recommendation available yet."}
    return opt.model_dump(mode="json")


@router.get("/energy/schedule", tags=["Energy"])
def energy_schedule():
    """Simulated optimized load schedule."""
    schedule = get_load_schedule()
    return {"schedule": [s.model_dump() for s in schedule]}


# ── WebSocket ─────────────────────────────────────────────────────────────────

@router.websocket("/ws/energy")
async def energy_stream(websocket: WebSocket):
    """Streams energy metrics every ENERGY_INTERVAL seconds."""
    await websocket.accept()
    _energy_clients.add(websocket)
    logger.info("⚡  Energy WebSocket connected  (active: %d)", len(_energy_clients))
    try:
        while True:
            metrics = generate_and_analyze_energy()
            opt     = get_latest_optimization()
            payload = json.dumps({
                "metrics":      metrics.model_dump(mode="json"),
                "optimization": opt.model_dump(mode="json") if opt else None,
            })
            await websocket.send_text(payload)
            await asyncio.sleep(ENERGY_INTERVAL)
    except WebSocketDisconnect:
        logger.info("⚡  Energy WebSocket disconnected")
    except Exception as exc:
        logger.error("Energy WebSocket error: %s", exc)
    finally:
        _energy_clients.discard(websocket)