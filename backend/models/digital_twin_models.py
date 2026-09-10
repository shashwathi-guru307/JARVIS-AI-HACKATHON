# digital_twin_models.py — Digital Twin state model
from pydantic import BaseModel
from datetime import datetime
from typing import Literal


class DigitalTwinState(BaseModel):
    """Real-time machine state for the Digital Twin visualization."""
    device_id: str
    status: Literal["HEALTHY", "WARNING", "DEGRADING", "HIGH_RISK", "CRITICAL", "OFFLINE"]
    health_score: float
    temperature: float
    vibration: float
    rpm: float
    battery: float
    active_alerts: int
    last_updated: datetime