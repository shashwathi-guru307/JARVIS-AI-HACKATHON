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