from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal


RiskLevel = Literal["NORMAL", "LOW", "MEDIUM", "HIGH", "CRITICAL"]


class SafetyStatus(BaseModel):
    device_id: str
    timestamp: datetime
    operator_present: bool
    activity_level: float = Field(..., ge=0.0, le=1.0)
    inactivity_duration_seconds: float = Field(..., ge=0.0)
    environmental_risk: RiskLevel
    fatigue_indicator: Literal["NONE", "POSSIBLE", "HIGH"]
    proximity_risk: RiskLevel
    emergency_status: Literal["NONE", "MANUAL_SOS", "SYSTEM_ALERT"]
    overall_risk: RiskLevel
    safety_score: float = Field(..., ge=0.0, le=100.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    recommended_action: str
    contributors: list[str] = []


class SafetyEvent(BaseModel):
    event_id: str
    device_id: str
    timestamp: datetime
    event_type: Literal[
        "INACTIVITY", "ENVIRONMENTAL_RISK", "PROXIMITY_RISK",
        "FATIGUE_PATTERN", "MANUAL_SOS", "SYSTEM_ALERT"
    ]
    severity: RiskLevel
    description: str
    recommended_action: str


class EmergencyRequest(BaseModel):
    device_id: str
    trigger: Literal["MANUAL_SOS", "SYSTEM_ALERT"]


class EmergencyResponse(BaseModel):
    status: str
    risk_level: RiskLevel
    recommended_action: str
    note: str