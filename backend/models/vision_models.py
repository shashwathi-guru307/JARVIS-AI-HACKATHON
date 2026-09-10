

    # vision_models.py — Pydantic models for computer vision analysis results
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal


class VisionAnalysis(BaseModel):
    """Structured result from one vision analysis cycle."""
    timestamp: datetime
    detected: bool
    event: str                             # e.g. "motion_detected", "scene_normal"
    objects: list[str] = []               # detected object labels (if any)
    risk_level: Literal["NORMAL", "WARNING", "CRITICAL"]
    summary: str
    recommended_action: str
    confidence: float = Field(..., ge=0.0, le=1.0)


class VisionStatus(BaseModel):
    """Current state of the vision subsystem."""
    camera: Literal["CONNECTED", "DISCONNECTED", "ERROR", "DEMO"]
    vision_mode: str
    processing: bool
    last_analysis: datetime | None = None