# maintenance_models.py — Pydantic models for predictive maintenance
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal


class HealthContributor(BaseModel):
    """One factor that contributed to the health score."""
    factor: str
    impact: float          # negative = bad, positive = good
    description: str


class MaintenancePrediction(BaseModel):
    """Full predictive maintenance assessment for one device."""
    device_id: str
    timestamp: datetime
    health_score: float = Field(..., ge=0.0, le=100.0)
    health_label: Literal["EXCELLENT", "GOOD", "WARNING", "POOR", "CRITICAL"]
    failure_risk: float = Field(..., ge=0.0, le=1.0)
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    maintenance_priority: Literal["ROUTINE", "SCHEDULED", "URGENT", "IMMEDIATE"]
    degradation_status: Literal["STABLE", "DEGRADING", "HIGH_RISK", "CRITICAL"]
    contributors: list[HealthContributor] = []
    recommendation: str
    ai_explanation: str | None = None


class MaintenanceHistoryEntry(BaseModel):
    timestamp: datetime
    health_score: float
    failure_risk: float
    degradation_status: str


class MaintenanceHistory(BaseModel):
    device_id: str
    history: list[MaintenanceHistoryEntry]