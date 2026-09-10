from datetime import datetime

from pydantic import BaseModel, Field


class TelemetryData(BaseModel):
    device_id: str
    timestamp: datetime

    temperature: float
    humidity: float = Field(..., ge=0, le=100)
    pressure: float
    vibration: float
    rpm: float = Field(..., ge=0)
    battery: float = Field(..., ge=0, le=100)


class TelemetryValues(BaseModel):
    temperature: float
    humidity: float
    pressure: float
    vibration: float
    rpm: float
    battery: float


class AnomalyAnalysis(BaseModel):
    status: str
    risk_level: str
    reasons: list[str]


class TelemetryResponse(BaseModel):
    device_id: str
    timestamp: datetime
    telemetry: TelemetryValues
    analysis: AnomalyAnalysis