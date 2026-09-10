import logging
from datetime import datetime, timezone
from fastapi import APIRouter
from backend.services.orchestrator import get_system_snapshot
from backend.utils.config import DEMO_MODE, AI_ENABLED, VISION_ENABLED

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", tags=["System"])
def health_check():
    return {
        "status": "online",
        "system": "J.A.R.V.I.S.",
        "version": "10.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "demo_mode": DEMO_MODE,
    }


@router.get("/system/status", tags=["System"])
def system_status():
    """Unified J.A.R.V.I.S. system status across all intelligence domains."""
    return get_system_snapshot()


@router.get("/system/health", tags=["System"])
def system_health():
    """Per-module health report."""
    snapshot = get_system_snapshot()
    return {
        "overall":      snapshot["system_status"],
        "modules":      snapshot["modules"],
        "system_score": snapshot["system_score"],
        "active_alerts": snapshot["active_alerts"],
        "ai_enabled":   AI_ENABLED,
        "vision_enabled": VISION_ENABLED,
        "demo_mode":    DEMO_MODE,
        "timestamp":    datetime.now(timezone.utc).isoformat(),
    }