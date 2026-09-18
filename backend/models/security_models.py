from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal


RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


class SecurityEvent(BaseModel):
    event_id:           str
    timestamp:          datetime
    event_type:         Literal[
        "AUTHENTICATION_FAILURE", "AUTHENTICATION_SUCCESS",
        "AUTHORIZATION_FAILURE", "RATE_LIMIT",
        "SUSPICIOUS_API_ACTIVITY", "SUSPICIOUS_TRANSACTION",
        "UNUSUAL_DEVICE", "UNUSUAL_LOCATION", "SYSTEM_ALERT"
    ]
    severity:           RiskLevel
    source:             str
    description:        str
    risk_score:         float = Field(..., ge=0.0, le=100.0)
    recommended_action: str


class SecurityStatus(BaseModel):
    security_status:  Literal["PROTECTED", "ELEVATED", "COMPROMISED"]
    authentication:   str
    authorization:    str
    rate_limiting:    str
    audit_logging:    str
    active_alerts:    int
    risk_level:       RiskLevel
    risk_score:       float = Field(..., ge=0.0, le=100.0)


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    role:         str
    username:     str


class AuditEntry(BaseModel):
    audit_id: str | None = None
    timestamp:  datetime
    event_type: str
    user_id:    str
    severity:   str
    description:str