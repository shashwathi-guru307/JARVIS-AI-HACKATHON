# predictive_service.py — orchestrates features → ML → health score → maintenance result
import logging
from collections import deque
from datetime import datetime, timezone
from backend.models.maintenance_models import (
    MaintenancePrediction, HealthContributor, MaintenanceHistoryEntry
)
from backend.models.digital_twin_models import DigitalTwinState
from backend.services.telemetry_storage import get_recent_telemetry, get_latest_telemetry
from backend.services.feature_service import engineer_features
from backend.vision.ml.predictive_model import predict

logger = logging.getLogger(__name__)

DEVICE_ID = "MACHINE_01"

# Rolling prediction history (for /maintenance/history)
_prediction_history: deque = deque(maxlen=200)
_latest_prediction: MaintenancePrediction | None = None


# ── Health scoring ────────────────────────────────────────────────────────────

def _calculate_health(features: dict) -> tuple[float, list[HealthContributor]]:
    """
    Map engineered features to a 0–100 health score with named contributors.
    Score starts at 100 and is penalised by each bad condition.
    """
    score = 100.0
    contributors: list[HealthContributor] = []

    def penalise(amount: float, factor: str, desc: str) -> None:
        nonlocal score
        score -= amount
        contributors.append(HealthContributor(factor=factor, impact=-amount, description=desc))

    temp = features["current_temperature"]
    if temp > 95:
        penalise(25, "Temperature", f"Critical temperature: {temp:.1f}°C")
    elif temp > 85:
        penalise(12, "Temperature", f"Elevated temperature: {temp:.1f}°C")

    vib = features["current_vibration"]
    if vib > 0.9:
        penalise(25, "Vibration", f"Critical vibration: {vib:.2f}g")
    elif vib > 0.6:
        penalise(12, "Vibration", f"Elevated vibration: {vib:.2f}g")

    if features["temperature_trend"] == "RISING":
        penalise(8, "Temperature trend", "Temperature is rising")

    if features["vibration_trend"] == "RISING":
        penalise(8, "Vibration trend", "Vibration is worsening")

    instability = features["rpm_instability"]
    if instability > 0.5:
        penalise(10, "RPM", f"High RPM instability: {instability:.2f}")
    elif instability > 0.2:
        penalise(5, "RPM", f"Moderate RPM instability: {instability:.2f}")

    bat = features["current_battery"]
    if bat < 10:
        penalise(15, "Battery", f"Critical battery: {bat:.0f}%")
    elif bat < 30:
        penalise(7, "Battery", f"Low battery: {bat:.0f}%")

    arate = features["anomaly_rate"]
    if arate > 0.3:
        penalise(10, "Anomalies", f"High anomaly rate: {arate:.0%}")
    elif arate > 0.1:
        penalise(5, "Anomalies", f"Moderate anomaly rate: {arate:.0%}")

    return max(score, 0.0), contributors


def _health_label(score: float) -> str:
    if score >= 90: return "EXCELLENT"
    if score >= 75: return "GOOD"
    if score >= 50: return "WARNING"
    if score >= 25: return "POOR"
    return "CRITICAL"


def _priority(risk_level: str) -> str:
    return {"LOW": "ROUTINE", "MEDIUM": "SCHEDULED", "HIGH": "URGENT", "CRITICAL": "IMMEDIATE"}.get(risk_level, "ROUTINE")


def _recommendation(risk_level: str, contributors: list[HealthContributor]) -> str:
    top = contributors[0].description if contributors else "current conditions"
    mapping = {
        "LOW":      "Machine operating normally. Continue routine monitoring.",
        "MEDIUM":   f"Early degradation detected ({top}). Schedule inspection within the next maintenance cycle.",
        "HIGH":     f"Persistent abnormalities detected ({top}). Schedule maintenance as soon as possible.",
        "CRITICAL": f"Multiple critical indicators active ({top}). Immediate inspection required.",
    }
    return mapping.get(risk_level, "Continue monitoring.")


# ── Public API ────────────────────────────────────────────────────────────────

def run_prediction() -> MaintenancePrediction:
    global _latest_prediction

    history = get_recent_telemetry(DEVICE_ID, n=100)
    features = engineer_features(history)
    ml_result = predict(features)

    health_score, contributors = _calculate_health(features)
    risk_level = ml_result["risk_level"]

    prediction = MaintenancePrediction(
        device_id=DEVICE_ID,
        timestamp=datetime.now(timezone.utc),
        health_score=round(health_score, 1),
        health_label=_health_label(health_score),
        failure_risk=ml_result["failure_risk"],
        risk_level=risk_level,
        maintenance_priority=_priority(risk_level),
        degradation_status=ml_result["degradation_status"],
        contributors=contributors,
        recommendation=_recommendation(risk_level, contributors),
    )

    _latest_prediction = prediction
    _prediction_history.append(
        MaintenanceHistoryEntry(
            timestamp=prediction.timestamp,
            health_score=prediction.health_score,
            failure_risk=prediction.failure_risk,
            degradation_status=prediction.degradation_status,
        )
    )

    if risk_level in ("HIGH", "CRITICAL"):
        logger.warning("🔧  %s | Health=%.0f | Risk=%s | %s",
                       DEVICE_ID, health_score, risk_level, prediction.degradation_status)
    else:
        logger.info("🔧  %s | Health=%.0f | Risk=%s | %s",
                    DEVICE_ID, health_score, risk_level, prediction.degradation_status)

    return prediction


def get_latest_prediction() -> MaintenancePrediction | None:
    return _latest_prediction


def get_prediction_history() -> list[MaintenanceHistoryEntry]:
    return list(_prediction_history)


def get_digital_twin() -> DigitalTwinState | None:
    latest = get_latest_telemetry(DEVICE_ID)
    pred   = _latest_prediction
    if not latest:
        return None

    deg = pred.degradation_status if pred else "STABLE"
    status_map = {
        "STABLE":    "HEALTHY",
        "DEGRADING": "DEGRADING",
        "HIGH_RISK": "HIGH_RISK",
        "CRITICAL":  "CRITICAL",
    }

    return DigitalTwinState(
        device_id=DEVICE_ID,
        status=status_map.get(deg, "WARNING"),
        health_score=pred.health_score if pred else 100.0,
        temperature=latest.temperature,
        vibration=latest.vibration,
        rpm=latest.rpm,
        battery=latest.battery,
        active_alerts=sum(1 for c in (pred.contributors if pred else []) if c.impact < -10),
        last_updated=latest.timestamp,
    )