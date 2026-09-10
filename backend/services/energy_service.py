import logging
from collections import deque
from datetime import datetime, timezone

from data.energy_generator import generate_energy
from backend.models.energy_models import (
    EnergyData, WastageResult, EnergyMetrics, EnergyOptimization,
    EnergyForecast, EnergyHistoryEntry, LoadScheduleSlot,
)

logger = logging.getLogger(__name__)

MAX_ENERGY_HISTORY = 500
_history: deque = deque(maxlen=MAX_ENERGY_HISTORY)
_latest_metrics: EnergyMetrics | None = None
_latest_optimization: EnergyOptimization | None = None


# ── Helpers ───────────────────────────────────────────────────────────────────

def _battery_state(charge_rate: float) -> str:
    if charge_rate > 0.1:   return "CHARGING"
    if charge_rate < -0.1:  return "DISCHARGING"
    return "IDLE"


def _efficiency_label(score: float) -> str:
    if score >= 90: return "EXCELLENT"
    if score >= 75: return "GOOD"
    if score >= 50: return "WARNING"
    return "POOR"


def _detect_wastage(data: EnergyData) -> WastageResult:
    """High consumption + low productive load = waste."""
    demand   = data.power_consumption_kw
    load_pct = data.load_percentage

    # Wasted power estimate: consumption above what load justifies
    expected_for_load = (load_pct / 100.0) * demand
    wasted = max(0.0, demand - expected_for_load - (data.solar_generation_kw * 0.1))
    wasted = round(wasted, 2)

    if demand > 24 and load_pct < 40:
        level = "HIGH"
        reason = f"High power consumption ({demand} kW) while machine utilization is only {load_pct:.0f}%"
    elif demand > 20 and load_pct < 55:
        level = "MEDIUM"
        reason = f"Elevated consumption ({demand} kW) relative to utilization ({load_pct:.0f}%)"
    elif wasted > 2.0:
        level = "LOW"
        reason = "Moderate energy wastage detected relative to productive load"
    else:
        level  = "NONE"
        reason = "Energy consumption is proportionate to machine utilization"
        wasted = 0.0

    return WastageResult(
        waste_detected=(level != "NONE"),
        waste_level=level,
        estimated_wasted_power_kw=wasted,
        reason=reason,
    )


def _calculate_efficiency(data: EnergyData, renewable_pct: float, wastage: WastageResult) -> float:
    """0–100 efficiency score based on renewable use, grid dependency, wastage, power factor."""
    score = 100.0

    # Penalise low renewable share
    if renewable_pct < 30:  score -= 20
    elif renewable_pct < 50: score -= 10
    elif renewable_pct < 70: score -= 5

    # Penalise grid dependency
    grid_dep = data.grid_power_kw / max(data.power_consumption_kw, 0.1) * 100
    if grid_dep > 70:   score -= 15
    elif grid_dep > 50: score -= 8

    # Penalise wastage
    if wastage.waste_level == "HIGH":   score -= 20
    elif wastage.waste_level == "MEDIUM": score -= 10
    elif wastage.waste_level == "LOW":    score -= 5

    # Penalise poor power factor
    if data.power_factor < 0.90: score -= 5

    # Reward high battery level (buffer available)
    if data.battery_level > 70: score += 5

    return round(max(0.0, min(100.0, score)), 1)


def _build_optimization(data: EnergyData, efficiency: float,
                         wastage: WastageResult, solar_surplus: float) -> EnergyOptimization:
    if solar_surplus > 3.0:
        return EnergyOptimization(
            optimization_status="RECOMMENDED",
            recommended_action="Solar generation exceeds current demand. Charge the battery or schedule flexible loads now.",
            estimated_saving_kw=round(solar_surplus * 0.7, 2),
            estimated_saving_percentage=round((solar_surplus / max(data.power_consumption_kw, 0.1)) * 70, 1),
            priority="MEDIUM",
        )
    if wastage.waste_level in ("HIGH", "MEDIUM"):
        return EnergyOptimization(
            optimization_status="URGENT",
            recommended_action=f"Reduce non-critical loads. {wastage.reason}.",
            estimated_saving_kw=wastage.estimated_wasted_power_kw,
            estimated_saving_percentage=round(
                (wastage.estimated_wasted_power_kw / max(data.power_consumption_kw, 0.1)) * 100, 1
            ),
            priority="HIGH",
        )
    if data.battery_level < 15:
        return EnergyOptimization(
            optimization_status="URGENT",
            recommended_action="Battery is critically low. Reduce flexible loads and allow battery to charge.",
            estimated_saving_kw=round(data.power_consumption_kw * 0.2, 2),
            estimated_saving_percentage=20.0,
            priority="HIGH",
        )
    if efficiency < 60:
        return EnergyOptimization(
            optimization_status="RECOMMENDED",
            recommended_action="Energy efficiency is low. Shift flexible loads to periods of higher solar generation.",
            estimated_saving_kw=round(data.power_consumption_kw * 0.15, 2),
            estimated_saving_percentage=15.0,
            priority="MEDIUM",
        )
    return EnergyOptimization(
        optimization_status="OPTIMAL",
        recommended_action="System is operating efficiently. Continue current load schedule.",
        estimated_saving_kw=0.0,
        estimated_saving_percentage=0.0,
        priority="LOW",
    )


# ── Public API ─────────────────────────────────────────────────────────────────

def generate_and_analyze_energy() -> EnergyMetrics:
    global _latest_metrics, _latest_optimization

    raw  = generate_energy()
    data = EnergyData(**raw)

    renewable_pct = round(
        (data.solar_generation_kw / max(data.power_consumption_kw, 0.01)) * 100, 1
    )
    renewable_pct = min(renewable_pct, 100.0)

    grid_dep      = round(
        (data.grid_power_kw / max(data.power_consumption_kw, 0.01)) * 100, 1
    )
    solar_surplus = round(max(0.0, data.solar_generation_kw - data.power_consumption_kw), 2)
    wastage       = _detect_wastage(data)
    efficiency    = _calculate_efficiency(data, renewable_pct, wastage)
    optimization  = _build_optimization(data, efficiency, wastage, solar_surplus)

    metrics = EnergyMetrics(
        device_id=data.device_id,
        timestamp=data.timestamp,
        current_demand_kw=data.power_consumption_kw,
        solar_generation_kw=data.solar_generation_kw,
        grid_power_kw=data.grid_power_kw,
        battery_level=data.battery_level,
        battery_state=_battery_state(data.battery_charge_rate),
        renewable_percentage=renewable_pct,
        grid_dependency=grid_dep,
        efficiency_score=efficiency,
        efficiency_label=_efficiency_label(efficiency),
        solar_surplus_kw=solar_surplus,
        wastage=wastage,
    )

    _history.append(EnergyHistoryEntry(
        timestamp=data.timestamp,
        power_consumption_kw=data.power_consumption_kw,
        solar_generation_kw=data.solar_generation_kw,
        efficiency_score=efficiency,
        battery_level=data.battery_level,
    ))

    if wastage.waste_level in ("HIGH", "MEDIUM"):
        logger.warning("⚡  Energy waste %s: %s", wastage.waste_level, wastage.reason)
    else:
        logger.info("⚡  Demand=%.1f kW  Solar=%.1f kW  Eff=%.0f",
                    data.power_consumption_kw, data.solar_generation_kw, efficiency)

    _latest_metrics      = metrics
    _latest_optimization = optimization
    return metrics


def get_latest_metrics() -> EnergyMetrics | None:
    return _latest_metrics


def get_latest_optimization() -> EnergyOptimization | None:
    return _latest_optimization


def get_energy_history() -> list[EnergyHistoryEntry]:
    return list(_history)


def get_energy_forecast() -> EnergyForecast | None:
    if len(_history) < 5:
        return None

    recent  = list(_history)[-30:]
    demands = [h.power_consumption_kw for h in recent]

    # Simple linear trend extrapolation
    import numpy as np
    x     = np.arange(len(demands), dtype=float)
    slope = float(np.polyfit(x, demands, 1)[0]) if len(demands) >= 2 else 0.0
    mean  = float(np.mean(demands))

    def forecast(minutes: int) -> float:
        steps  = minutes * 60   # seconds
        return round(max(0.5, mean + slope * steps), 2)

    trend_label = "RISING" if slope > 0.001 else ("FALLING" if slope < -0.001 else "STABLE")
    confidence  = round(min(0.95, 0.5 + len(recent) / 60), 2)

    return EnergyForecast(
        current_demand_kw=demands[-1],
        forecast_5min_kw=forecast(5),
        forecast_10min_kw=forecast(10),
        forecast_15min_kw=forecast(15),
        confidence=confidence,
        trend=trend_label,
    )


def get_load_schedule() -> list[LoadScheduleSlot]:
    """Return a simulated optimized load schedule based on current conditions."""
    m = _latest_metrics
    if m is None:
        return []

    schedule: list[LoadScheduleSlot] = []

    # Morning — usually solar building up
    schedule.append(LoadScheduleSlot(
        start_time="06:00", end_time="09:00",
        action="NORMAL OPERATION",
        priority="IMPORTANT",
        reason="Morning ramp — solar generation beginning",
    ))

    # Midday — solar peak
    if m.solar_generation_kw > m.current_demand_kw * 0.8:
        schedule.append(LoadScheduleSlot(
            start_time="10:00", end_time="14:00",
            action="RUN FLEXIBLE LOADS",
            priority="FLEXIBLE",
            reason="Solar generation is high — ideal for flexible workloads",
        ))
    else:
        schedule.append(LoadScheduleSlot(
            start_time="10:00", end_time="14:00",
            action="NORMAL OPERATION",
            priority="IMPORTANT",
            reason="Moderate solar — normal operation recommended",
        ))

    # Afternoon — potential peak
    if m.current_demand_kw > 22:
        schedule.append(LoadScheduleSlot(
            start_time="14:00", end_time="17:00",
            action="REDUCE OPTIONAL LOADS",
            priority="OPTIONAL",
            reason="Demand is elevated — shed non-critical loads",
        ))
    else:
        schedule.append(LoadScheduleSlot(
            start_time="14:00", end_time="17:00",
            action="NORMAL OPERATION",
            priority="IMPORTANT",
            reason="Demand within normal range",
        ))

    # Evening — solar falling
    schedule.append(LoadScheduleSlot(
        start_time="18:00", end_time="21:00",
        action="MINIMIZE NON-ESSENTIAL LOADS",
        priority="FLEXIBLE",
        reason="Solar generation declining — rely on battery and minimize grid draw",
    ))

    # Night
    schedule.append(LoadScheduleSlot(
        start_time="21:00", end_time="06:00",
        action="CRITICAL SYSTEMS ONLY",
        priority="CRITICAL",
        reason="Night period — run only essential systems",
    ))

    return schedule