# maintenance.py — predictive maintenance + digital twin API endpoints
import asyncio
import logging
from fastapi import APIRouter, BackgroundTasks
from backend.services.predictive_service import (
    run_prediction,
    get_latest_prediction,
    get_prediction_history,
    get_digital_twin,
)
from backend.utils.config import get_prediction_interval

logger = logging.getLogger(__name__)
router = APIRouter()

_prediction_task_started = False


async def _prediction_loop() -> None:
    """Background task — runs prediction every PREDICTION_INTERVAL seconds."""
    interval = get_prediction_interval()
    while True:
        try:
            run_prediction()
        except Exception as exc:
            logger.error("Prediction loop error: %s", exc)
        await asyncio.sleep(interval)


@router.on_event("startup")
async def start_prediction_loop() -> None:
    global _prediction_task_started
    if not _prediction_task_started:
        asyncio.create_task(_prediction_loop())
        _prediction_task_started = True
        logger.info("🔧  Predictive maintenance loop started (interval=%ds)", get_prediction_interval())


@router.get("/maintenance/status", tags=["Maintenance"])
def maintenance_status():
    """Current machine health and maintenance prediction."""
    pred = get_latest_prediction()
    if pred is None:
        return {"message": "No prediction available yet — wait a few seconds for the first cycle."}
    return pred.model_dump(mode="json")


@router.get("/maintenance/history", tags=["Maintenance"])
def maintenance_history():
    """Recent health and failure-risk history."""
    history = get_prediction_history()
    return {"device_id": "MACHINE_01", "history": [h.model_dump(mode="json") for h in history]}


@router.get("/maintenance/recommendation", tags=["Maintenance"])
def maintenance_recommendation():
    """Latest maintenance recommendation."""
    pred = get_latest_prediction()
    if pred is None:
        return {"recommendation": "No data yet. Please wait for telemetry to accumulate."}
    return {
        "device_id": pred.device_id,
        "recommendation": pred.recommendation,
        "risk_level": pred.risk_level,
        "contributors": [c.model_dump() for c in pred.contributors],
    }


@router.get("/digital-twin/{device_id}", tags=["Digital Twin"])
def digital_twin(device_id: str):
    """Current Digital Twin state for a device."""
    twin = get_digital_twin()
    if twin is None or twin.device_id != device_id:
        return {"message": f"No telemetry found for device '{device_id}'."}
    return twin.model_dump(mode="json")