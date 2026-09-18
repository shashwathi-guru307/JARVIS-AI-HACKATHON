"""
Event Correlation Engine — identifies compound threats by matching
simultaneous elevated-risk conditions across domains.
All rules are explicit and explainable.
"""
from backend.services.predictive_service import get_latest_prediction
from backend.services.safety_service import get_latest_safety
from backend.services.security_service import get_security_status
from backend.services.transaction_risk_service import get_transaction_risks
from backend.services.energy_service import get_latest_metrics as get_latest_energy
from backend.services.telemetry_storage import get_latest_telemetry
from backend.models.event_models import IntelligenceEvent
from datetime import datetime, timezone
import uuid


def correlate_events() -> list[str]:
    """
    Check active correlation rules and return a list of plain-language
    correlated condition strings. Returns [] when no meaningful correlation exists.
    """
    correlations: list[str] = []

    pred   = get_latest_prediction()
    safety = get_latest_safety()
    sec    = get_security_status()
    energy = get_latest_energy()
    tx     = get_transaction_risks(5)
    tel    = get_latest_telemetry("MACHINE_01")

    machine_high = pred and pred.risk_level in ("HIGH", "CRITICAL")
    safety_high  = safety and safety.overall_risk in ("HIGH", "CRITICAL")
    prox_high    = safety and safety.proximity_risk in ("HIGH", "CRITICAL")
    sec_high     = sec.risk_level in ("HIGH", "CRITICAL")
    tx_suspicious = any(r.is_suspicious for r in tx)
    energy_high  = energy and energy.efficiency_score < 60
    temp_high    = tel and tel.temperature > 85
    vib_high     = tel and tel.vibration > 0.6

    # Rule 1: Machine degradation + operator proximity
    if machine_high and prox_high:
        correlations.append(
            "High machine failure risk coincides with possible operator proximity — elevated safety concern"
        )

    # Rule 2: Machine degradation + safety risk
    if machine_high and safety_high and not prox_high:
        correlations.append(
            "Machine risk and overall safety risk are simultaneously elevated"
        )

    # Rule 3: Temperature + vibration compound
    if temp_high and vib_high:
        correlations.append(
            "Elevated temperature and vibration occurring together — increased mechanical stress risk"
        )

    # Rule 4: Security anomaly + suspicious transaction
    if sec_high and tx_suspicious:
        correlations.append(
            "Unusual API/authentication activity coincides with a suspicious transaction pattern — security review required"
        )

    # Rule 5: High energy demand + machine high load
    if energy_high and machine_high:
        correlations.append(
            "High machine operational load is contributing to elevated energy demand and reduced efficiency"
        )

    # Rule 6: Machine + energy + safety triple
    if machine_high and energy_high and safety_high:
        correlations.append(
            "Machine, energy, and safety risks are all elevated simultaneously — multi-domain operational concern"
        )

    # Rule 7: Security + machine
    if sec_high and machine_high:
        correlations.append(
            "Security anomalies are occurring during a period of elevated machine risk"
        )

    return correlations


def normalize_events() -> list[IntelligenceEvent]:
    """Normalize the latest heterogeneous domain readings into canonical events."""
    events: list[IntelligenceEvent] = []
    now = datetime.now(timezone.utc)
    telemetry = get_latest_telemetry("MACHINE_01")
    prediction = get_latest_prediction()

    if telemetry and telemetry.temperature > 85:
        severity = "CRITICAL" if telemetry.temperature >= 95 else "HIGH"
        events.append(IntelligenceEvent(
            event_id=f"evt-{uuid.uuid4().hex[:12]}", timestamp=telemetry.timestamp,
            source="TELEMETRY", event_type="ELEVATED_TEMPERATURE", severity=severity,
            risk_score=min(100, telemetry.temperature), device_id=telemetry.device_id,
            title="Elevated machine temperature",
            description=f"Temperature reached {telemetry.temperature:.1f}°C.",
            contributing_factors=["temperature threshold exceeded"],
            recommended_action="Reduce simulated load and inspect machine.",
        ))
    if telemetry and telemetry.vibration > 0.6:
        severity = "CRITICAL" if telemetry.vibration >= 0.9 else "HIGH"
        events.append(IntelligenceEvent(
            event_id=f"evt-{uuid.uuid4().hex[:12]}", timestamp=telemetry.timestamp,
            source="TELEMETRY", event_type="ELEVATED_VIBRATION", severity=severity,
            risk_score=min(100, telemetry.vibration * 100), device_id=telemetry.device_id,
            title="Elevated machine vibration",
            description=f"Vibration reached {telemetry.vibration:.2f}g.",
            contributing_factors=["vibration threshold exceeded"],
            recommended_action="Reduce simulated load and inspect machine.",
        ))
    if telemetry and telemetry.rpm > 2100:
        events.append(IntelligenceEvent(
            event_id=f"evt-{uuid.uuid4().hex[:12]}", timestamp=telemetry.timestamp,
            source="TELEMETRY", event_type="ABNORMAL_RPM", severity="HIGH",
            risk_score=75, device_id=telemetry.device_id,
            title="Abnormal machine speed",
            description=f"RPM reached {telemetry.rpm:.0f}, outside the configured demo operating band.",
            contributing_factors=["RPM deviation threshold exceeded"],
            recommended_action="Reduce simulated load and inspect machine.",
        ))
    if prediction and (prediction.risk_level in ("HIGH", "CRITICAL") or (telemetry and telemetry.temperature > 85 and telemetry.vibration > 0.6)):
        events.append(IntelligenceEvent(
            event_id=f"evt-{uuid.uuid4().hex[:12]}", timestamp=prediction.timestamp,
            source="MAINTENANCE", event_type="PREDICTIVE_DEGRADATION", severity=prediction.risk_level,
            risk_score=round((1 - prediction.health_score / 100) * 100, 1), device_id=prediction.device_id,
            title="Predictive maintenance degradation",
            description=prediction.degradation_status.replace("_", " ").title(),
            contributing_factors=[c.description for c in prediction.contributors],
            recommended_action=prediction.recommendation,
        ))
    return events


def get_correlated_event_groups() -> list[dict]:
    """Return structured correlation groups for incident creation."""
    events = normalize_events()
    by_type = {event.event_type: event for event in events}
    if {"ELEVATED_TEMPERATURE", "ELEVATED_VIBRATION"}.issubset(by_type):
        selected = [by_type[key] for key in ("ELEVATED_TEMPERATURE", "ELEVATED_VIBRATION")]
        if "ABNORMAL_RPM" in by_type:
            selected.append(by_type["ABNORMAL_RPM"])
        if "PREDICTIVE_DEGRADATION" in by_type:
            selected.append(by_type["PREDICTIVE_DEGRADATION"])
        return [{
            "events": selected,
            "conditions": ["elevated temperature", "elevated vibration"] + (["abnormal RPM"] if "ABNORMAL_RPM" in by_type else []) + (["predictive maintenance degradation"] if "PREDICTIVE_DEGRADATION" in by_type else []),
            "components": ["MACHINE_01", "thermal subsystem", "mechanical subsystem"],
            "title": "Machine degradation and overheating",
        }]
    if len(events) >= 2:
        return [{
            "events": events,
            "conditions": correlate_events(),
            "components": sorted({event.device_id for event in events if event.device_id}),
            "title": "Correlated operational incident",
        }]
    return []