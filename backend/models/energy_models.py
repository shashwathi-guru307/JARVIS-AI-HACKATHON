from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class EnergyData(BaseModel):
    device_id: str
    timestamp: datetime

    power_consumption_kw: float = Field(..., ge=0.0)
    energy_consumed_kwh: float = Field(..., ge=0.0)
    solar_generation_kw: float = Field(..., ge=0.0)
    grid_power_kw: float = Field(..., ge=0.0)

    battery_level: float = Field(..., ge=0.0, le=100.0)

    # Positive = charging, negative = discharging
    battery_charge_rate: float

    load_percentage: float = Field(..., ge=0.0, le=100.0)
    power_factor: float = Field(..., ge=0.0, le=1.0)


class WastageResult(BaseModel):
    waste_detected: bool
    waste_level: Literal["NONE", "LOW", "MEDIUM", "HIGH"]
    estimated_wasted_power_kw: float
    reason: str


class EnergyMetrics(BaseModel):
    device_id: str
    timestamp: datetime

    current_demand_kw: float
    solar_generation_kw: float
    grid_power_kw: float

    battery_level: float
    battery_state: Literal["CHARGING", "DISCHARGING", "IDLE"]

    # 0–100
    renewable_percentage: float

    # 0–100
    grid_dependency: float

    # 0–100
    efficiency_score: float

    efficiency_label: Literal[
        "EXCELLENT",
        "GOOD",
        "WARNING",
        "POOR",
    ]

    solar_surplus_kw: float
    wastage: WastageResult


class EnergyOptimization(BaseModel):
    optimization_status: Literal[
        "OPTIMAL",
        "RECOMMENDED",
        "URGENT",
    ]

    recommended_action: str

    estimated_saving_kw: float
    estimated_saving_percentage: float

    priority: Literal[
        "LOW",
        "MEDIUM",
        "HIGH",
    ]


class EnergyForecast(BaseModel):
    current_demand_kw: float

    forecast_5min_kw: float
    forecast_10min_kw: float
    forecast_15min_kw: float

    confidence: float

    trend: Literal[
        "STABLE",
        "RISING",
        "FALLING",
    ]


class EnergyHistoryEntry(BaseModel):
    timestamp: datetime

    power_consumption_kw: float
    solar_generation_kw: float
    efficiency_score: float
    battery_level: float


class LoadScheduleSlot(BaseModel):
    start_time: str
    end_time: str

    action: str

    priority: Literal[
        "CRITICAL",
        "IMPORTANT",
        "FLEXIBLE",
        "OPTIONAL",
    ]

    reason: str