import logging
import uuid
from collections import deque
from datetime import datetime, timezone

from data.safety_generator import generate_safety
from backend.models.safety_models import SafetyStatus, SafetyEvent, EmergencyResponse
from backend.services.telemetry_storage import get_latest_telemetry
from backend.services.predictive_service import get_latest_prediction

logger = logging.getLogger(__name__)

MAX_SAFETY_HISTORY = 200
_history: deque = deque(maxlen=MAX_SAFETY_HISTORY)
_events:  deque = deque(maxlen=100)
_latest_status: SafetyStatus | None = None
_emergency_active = False

RISK_ORDER = ["NORMAL", "LOW", "MEDIUM", "HIGH", "CRITICAL"]


def _max_risk(*risks: str) -> str:
    return max(risks, key=lambda r: RISK_ORDER.index(r) if r in RISK_ORDER else 0)


def _safety_score(overall_risk: str, contributors: list[str]) -> float:
    base = 100.0
    penalties = {"NORMAL": 0, "LOW": 8, "MEDIUM": 18, "HIGH": 30, "CRITICAL": 50}
    score = base - penalties.get(overall_risk, 0) - len(contributors) * 3
    return round(max(0.0, min(100.0, score)), 1)


def _recommendation(overall_risk: str, raw: dict) -> str:
    if raw["emergency_status"] != "NONE":
        return "Critical safety event detected. Follow the site's emergency procedure immediately."
    if raw["proximity_risk"] in ("HIGH", "CRITICAL"):
        return ("Possible operator proximity detected near equipment operating under elevated-risk conditions. "
                "Verify safe operating distance.")
    if raw["environmental_risk"] in ("HIGH", "CRITICAL"):
        return "Environmental conditions require attention. Inspect the operating area."
    if raw["fatigue_indicator"] == "HIGH":
        return ("Possible fatigue-related pattern detected. "
                "Consider taking a break or verifying operator status.")
    if raw["inactivity_duration_seconds"] > 300:
        return "Extended inactivity detected. Verify operator status."
    if overall_risk in ("MEDIUM", "HIGH"):
        return "Safety conditions require monitoring. Verify operating environment."
    return "Continue normal monitoring."


def _build_contributors(raw: dict, telemetry=None, pred=None) -> list[str]:
    factors = []
    if raw["emergency_status"] != "NONE":
        factors.append("Emergency event active")
    if raw["proximity_risk"] in ("HIGH", "CRITICAL"):
        factors.append("Possible operator proximity to equipment")
    if raw["environmental_risk"] in ("HIGH", "CRITICAL"):
        factors.append(f"Environmental risk: {raw['environmental_risk']}")
    if raw["fatigue_indicator"] in ("POSSIBLE", "HIGH"):
        factors.append("Possible fatigue-related activity pattern detected")
    if raw["inactivity_duration_seconds"] > 300:
        factors.append(f"Extended inactivity: {raw['inactivity_duration_seconds']:.0f}s")

    # Integrate telemetry
    if telemetry:
        if telemetry.temperature > 90:
            factors.append(f"High machine temperature: {telemetry.temperature:.1f}°C")
        if telemetry.vibration > 0.75:
            factors.append(f"High machine vibration: {telemetry.vibration:.2f}g")

    # Integrate predictive maintenance
    if pred and pred.risk_level in ("HIGH", "CRITICAL"):
        factors.append(f"Machine failure risk {pred.risk_level}: health score {pred.health_score:.0f}/100")

    return factors


def _emit_event(device_id: str, event_type: str, severity: str, description: str, action: str) -> SafetyEvent:
    event = SafetyEvent(
        event_id=str(uuid.uuid4())[:8],
        device_id=device_id,
        timestamp=datetime.now(timezone.utc),
        event_type=event_type,
        severity=severity,
        description=description,
        recommended_action=action,
    )
    _events.appendleft(event)
    logger.warning("🛡  Safety event [%s] %s: %s", severity, event_type, description)
    return event


# ── Public API ────────────────────────────────────────────────────────────────

def generate_and_analyze_safety() -> SafetyStatus:
    global _latest_status

    raw      = generate_safety()
    telemetry = get_latest_telemetry(raw["device_id"])
    pred      = get_latest_prediction()

    # Pull machine-level risk from telemetry/prediction
    machine_risk = "NORMAL"
    if pred:
        machine_risk = pred.risk_level
    elif telemetry:
        if telemetry.temperature > 95 or telemetry.vibration > 0.9:
            machine_risk = "HIGH"
        elif telemetry.temperature > 85 or telemetry.vibration > 0.6:
            machine_risk = "MEDIUM"

    emergency_risk = "CRITICAL" if raw["emergency_status"] != "NONE" else "NORMAL"

    overall_risk = _max_risk(
        raw["environmental_risk"],
        raw["proximity_risk"],
        machine_risk,
        emergency_risk,
        "LOW" if raw["inactivity_duration_seconds"] > 300 else "NORMAL",
    )

    contributors = _build_contributors(raw, telemetry, pred)
    score        = _safety_score(overall_risk, contributors)
    action       = _recommendation(overall_risk, raw)
    confidence   = round(0.70 + (len(contributors) * 0.03), 2)
    confidence   = min(confidence, 0.97)

    status = SafetyStatus(
        device_id=raw["device_id"],
        timestamp=datetime.fromisoformat(raw["timestamp"]),
        operator_present=raw["operator_present"],
        activity_level=raw["activity_level"],
        inactivity_duration_seconds=raw["inactivity_duration_seconds"],
        environmental_risk=raw["environmental_risk"],
        fatigue_indicator=raw["fatigue_indicator"],
        proximity_risk=raw["proximity_risk"],
        emergency_status=raw["emergency_status"],
        overall_risk=overall_risk,
        safety_score=score,
        confidence=confidence,
        recommended_action=action,
        contributors=contributors,
    )

    # Emit discrete events for significant changes
    if raw["emergency_status"] != "NONE":
        _emit_event(raw["device_id"], "MANUAL_SOS", "CRITICAL",
                    "Emergency SOS event activated.", action)
    elif overall_risk in ("HIGH", "CRITICAL"):
        _emit_event(raw["device_id"], "SYSTEM_ALERT", overall_risk,
                    f"Overall safety risk: {overall_risk}. {contributors[0] if contributors else ''}",
                    action)

    _history.appendleft(status)
    _latest_status = status

    if overall_risk in ("HIGH", "CRITICAL"):
        logger.warning("🛡  Safety risk %s | Score %.0f | %s", overall_risk, score, action)
    else:
        logger.info("🛡  Safety OK | Score %.0f", score)

    return status


def get_latest_safety() -> SafetyStatus | None:
    return _latest_status


def get_safety_history() -> list[SafetyStatus]:
    return list(_history)


def get_safety_events() -> list[SafetyEvent]:
    return list(_events)


def trigger_emergency(device_id: str, trigger: str) -> EmergencyResponse:
    global _emergency_active
    _emergency_active = True
    _emit_event(device_id, "MANUAL_SOS", "CRITICAL",
                f"Manual emergency triggered: {trigger}",
                "Follow the site's emergency procedure immediately.")
    logger.critical("🚨  EMERGENCY TRIGGERED: %s / %s", device_id, trigger)
    return EmergencyResponse(
        status="EMERGENCY_ACTIVE",
        risk_level="CRITICAL",
        recommended_action="Follow the site's emergency procedure immediately.",
        note="⚠ This is a simulated emergency for demonstration purposes only. "
             "Do not contact real emergency services based on this alert.",
    )


def reset_emergency() -> dict:
    global _emergency_active
    _emergency_active = False
    logger.info("🛡  Emergency reset")
    return {"status": "EMERGENCY_CLEARED"}