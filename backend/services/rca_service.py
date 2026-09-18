from backend.services.predictive_service import get_latest_prediction
from backend.services.telemetry_storage import get_latest_telemetry


def analyze_root_cause(events: list[dict]) -> dict:
    telemetry = get_latest_telemetry("MACHINE_01")
    prediction = get_latest_prediction()
    evidence = [event["description"] for event in events]
    factors = []
    if telemetry and telemetry.temperature > 85:
        factors.append(f"Elevated temperature ({telemetry.temperature:.1f}°C)")
    if telemetry and telemetry.vibration > 0.6:
        factors.append(f"Elevated vibration ({telemetry.vibration:.2f}g)")
    if telemetry and telemetry.rpm > 2100:
        factors.append(f"RPM deviated from the configured operating band ({telemetry.rpm:.0f})")
    if prediction and prediction.risk_level in ("HIGH", "CRITICAL"):
        factors.append(f"Predictive maintenance risk is {prediction.risk_level}")

    mechanical = len(factors) >= 2
    return {
        "probable_root_causes": [
            "Mechanical degradation, possibly bearing-related, causing increased friction/load."
            if mechanical else "The correlated operating conditions require further investigation."
        ],
        "contributing_factors": factors,
        "evidence": evidence + factors,
        "confidence": 0.86 if mechanical and len(factors) >= 3 else 0.68 if mechanical else 0.45,
        "alternatives": [
            "Sensor calibration drift",
            "Temporary load or process variation",
        ],
    }