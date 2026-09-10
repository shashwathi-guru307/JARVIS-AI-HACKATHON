from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Transaction(BaseModel):
    transaction_id: str
    timestamp: datetime
    user_id: str
    amount: float = Field(..., gt=0)
    currency: str = Field(..., min_length=1)
    transaction_type: str
    merchant_category: str
    location: str
    device_id: str
    is_rapid: bool = False


class TransactionRisk(BaseModel):
    transaction_id: str
    timestamp: datetime
    risk_score: float = Field(..., ge=0.0, le=100.0)
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    contributors: list[str]
    recommendation: str
    is_suspicious: bool


class TransactionSummary(BaseModel):
    total_count: int
    high_risk: int
    medium_risk: int
    low_risk: int
    total_amount: float
    avg_amount: float
    risk_trend: Literal["STABLE", "RISING", "FALLING"]