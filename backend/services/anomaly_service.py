from backend.models.telemetry_models import TelemetryData


# ============================================================
# CONFIGURABLE THRESHOLDS
# ============================================================

THRESHOLDS = {
    "temperature": {
        "warning": 85,
        "critical": 95,
    },
    "vibration": {
        "warning": 0.60,
        "critical": 0.90,
    },
    "battery": {
        "warning": 30,
        "critical": 10,
    },
}


def detect_anomaly(data: TelemetryData) -> dict:
    """
    Analyze telemetry data using rule-based thresholds.

    Returns:
        {
            "status": "NORMAL | WARNING | CRITICAL",
            "risk_level": "LOW | MEDIUM | HIGH | CRITICAL",
            "reasons": [...]
        }
    """

    reasons = []
    statuses = []

    # ========================================================
    # TEMPERATURE
    # ========================================================

    if data.temperature > THRESHOLDS["temperature"]["critical"]:
        statuses.append("CRITICAL")
        reasons.append("Temperature is critically high")

    elif data.temperature >= THRESHOLDS["temperature"]["warning"]:
        statuses.append("WARNING")
        reasons.append("Temperature is above normal range")


    # ========================================================
    # VIBRATION
    # ========================================================

    if data.vibration > THRESHOLDS["vibration"]["critical"]:
        statuses.append("CRITICAL")
        reasons.append("Vibration is critically high")

    elif data.vibration >= THRESHOLDS["vibration"]["warning"]:
        statuses.append("WARNING")
        reasons.append("Vibration is elevated")


    # ========================================================
    # BATTERY
    # ========================================================

    if data.battery < THRESHOLDS["battery"]["critical"]:
        statuses.append("CRITICAL")
        reasons.append("Battery level is critically low")

    elif data.battery <= THRESHOLDS["battery"]["warning"]:
        statuses.append("WARNING")
        reasons.append("Battery level is low")


    # ========================================================
    # DETERMINE OVERALL STATUS
    # ========================================================

    if "CRITICAL" in statuses:
        status = "CRITICAL"
        risk_level = "CRITICAL"

    elif "WARNING" in statuses:
        status = "WARNING"
        risk_level = "HIGH"

    else:
        status = "NORMAL"
        risk_level = "LOW"


    return {
        "status": status,
        "risk_level": risk_level,
        "reasons": reasons,
    }