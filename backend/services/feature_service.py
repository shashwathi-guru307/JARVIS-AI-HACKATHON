# feature_service.py — engineers machine-health features from telemetry history
import numpy as np
from backend.models.telemetry_models import TelemetryData


def _slope(values: list[float]) -> float:
    """Linear regression slope over an index range. Positive = rising."""
    if len(values) < 2:
        return 0.0
    x = np.arange(len(values), dtype=float)
    y = np.array(values, dtype=float)
    return float(np.polyfit(x, y, 1)[0])


def _trend_label(slope: float, threshold: float = 0.05) -> str:
    if slope > threshold:
        return "RISING"
    if slope < -threshold:
        return "FALLING"
    return "STABLE"


def engineer_features(history: list[TelemetryData]) -> dict:
    """
    Compute machine-health features from a list of recent TelemetryData.

    Returns a flat dict suitable for ML prediction or rule-based scoring.
    """
    if not history:
        return _empty_features()

    temps = [r.temperature for r in history]
    vibs  = [r.vibration   for r in history]
    rpms  = [r.rpm         for r in history]
    bats  = [r.battery     for r in history]

    temp_slope = _slope(temps[-30:])
    vib_slope  = _slope(vibs[-30:])
    rpm_slope  = _slope(rpms[-30:])
    bat_slope  = _slope(bats[-30:])

    rpm_variance   = float(np.var(rpms[-30:])) if len(rpms) >= 2 else 0.0
    rpm_instability = min(rpm_variance / 10000.0, 1.0)   # normalised 0–1

    # Simple anomaly count from recent history
    anomaly_count = sum(
        1 for r in history[-50:]
        if r.temperature > 85 or r.vibration > 0.60 or r.rpm > 2100
    )
    anomaly_rate = anomaly_count / max(len(history[-50:]), 1)

    return {
        # Temperature
        "current_temperature":    temps[-1],
        "temperature_mean":       float(np.mean(temps)),
        "temperature_max":        float(np.max(temps)),
        "temperature_trend":      _trend_label(temp_slope),
        "temperature_slope":      round(temp_slope, 4),

        # Vibration
        "current_vibration":      vibs[-1],
        "vibration_mean":         float(np.mean(vibs)),
        "vibration_max":          float(np.max(vibs)),
        "vibration_trend":        _trend_label(vib_slope, threshold=0.002),
        "vibration_slope":        round(vib_slope, 4),

        # RPM
        "current_rpm":            rpms[-1],
        "rpm_mean":               float(np.mean(rpms)),
        "rpm_variance":           round(rpm_variance, 2),
        "rpm_instability":        round(rpm_instability, 4),
        "rpm_trend":              _trend_label(rpm_slope, threshold=1.0),

        # Battery
        "current_battery":        bats[-1],
        "battery_slope":          round(bat_slope, 4),

        # Composite
        "anomaly_count":          anomaly_count,
        "anomaly_rate":           round(anomaly_rate, 4),
        "history_length":         len(history),
    }


def _empty_features() -> dict:
    return {
        "current_temperature": 72.0, "temperature_mean": 72.0, "temperature_max": 72.0,
        "temperature_trend": "STABLE", "temperature_slope": 0.0,
        "current_vibration": 0.3,  "vibration_mean": 0.3,  "vibration_max": 0.3,
        "vibration_trend": "STABLE", "vibration_slope": 0.0,
        "current_rpm": 1800.0, "rpm_mean": 1800.0, "rpm_variance": 0.0,
        "rpm_instability": 0.0, "rpm_trend": "STABLE",
        "current_battery": 90.0, "battery_slope": 0.0,
        "anomaly_count": 0, "anomaly_rate": 0.0, "history_length": 0,
    }