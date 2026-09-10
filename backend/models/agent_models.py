# agent_models.py — Pydantic models for request and response validation
from pydantic import BaseModel, Field
from typing import Literal
class AnalyzeRequest(BaseModel):
    """Incoming request: a single message describing an event or sensor reading."""
    message: str = Field(
        ...,
        min_length=1,
        description="The event or sensor reading to analyze.",
        examples=["Machine temperature is 96°C and vibration is 0.92"]
    )


class AgentResponse(BaseModel):
    """Structured JSON response returned by J.A.R.V.I.S."""
    status: Literal["success", "error"]
    risk_level: Literal["NORMAL", "LOW", "MEDIUM", "HIGH", "CRITICAL"] | None = None
    summary: str | None = None
    reason: str | None = None
    recommended_action: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    # Only present on error responses
    error: str | None = None