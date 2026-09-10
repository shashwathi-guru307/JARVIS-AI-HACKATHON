# health.py — simple health check, always available
from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["Health"])
def health_check() -> dict:
    """
    Returns system status. Works even if the AI API is unavailable.
    """
    return {
        "status": "online",
        "system": "J.A.R.V.I.S.",
        "version": "1.0.0"
    }