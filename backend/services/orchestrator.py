"""
J.A.R.V.I.S. Orchestrator — central coordinator that collects context
from all intelligence domains, runs correlation and risk calculation,
and produces a unified system state snapshot.
"""
import logging
from datetime import datetime, timezone

from backend.services.risk_engine import calculate_system_risk
from backend.services.correlation_service import correlate_events
from backend.services.predictive_service import get_latest_prediction
from backend.services.energy_service import get_latest_metrics as get_latest_energy
from backend.services.safety_service import get_latest_safety
from backend.services.security_service import get_security_status
from backend.services.transaction_risk_service import get_transaction_summary
from backend.services.telemetry_storage import get_latest_telemetry
from backend.services.incident_service import list_incidents

logger = logging.getLogger(__name__)


def get_system_snapshot() -> dict:
    """
    Collect context from all domains and return a unified system state dict.
    Every field comes from the actual running services — nothing is invented.
    """
    risk_data    = calculate_system_risk()
    correlations = correlate_events()

    pred   = get_latest_prediction()
    energy = get_latest_energy()
    safety = get_latest_safety()
    sec    = get_security_status()
    tx     = get_transaction_summary()
    tel    = get_latest_telemetry("MACHINE_01")

    active_alerts = (
        (1 if pred and pred.risk_level in ("HIGH", "CRITICAL") else 0) +
        (1 if energy and energy.efficiency_score < 60 else 0) +
        (1 if safety and safety.overall_risk in ("HIGH", "CRITICAL") else 0) +
        (1 if sec.risk_level in ("HIGH", "CRITICAL") else 0) +
        (1 if tx and tx.high_risk > 0 else 0)
    )

    system_status = (
        "CRITICAL"     if risk_data["system_risk"] == "CRITICAL" else
        "DEGRADED"     if risk_data["system_risk"] == "HIGH"     else
        "CAUTION"      if risk_data["system_risk"] == "MEDIUM"   else
        "OPERATIONAL"
    )

    priority = (
        "IMMEDIATE" if risk_data["system_risk"] == "CRITICAL" else
        "URGENT"    if risk_data["system_risk"] == "HIGH"     else
        "REVIEW"    if risk_data["system_risk"] == "MEDIUM"   else
        "MONITOR"
    )

    snapshot = {
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "system_status":   system_status,
        "system_risk":     risk_data["system_risk"],
        "system_score":    risk_data["system_score"],
        "priority":        priority,
        "active_alerts":   active_alerts,
        "correlated_conditions": correlations,
        "recommendation":  risk_data["recommendation"],
        "domain_risks":    risk_data["domain_risks"],
        "contributing_factors": risk_data["contributing"],
        "active_incidents": [incident.model_dump(mode="json") for incident in list_incidents() if incident.status not in ("RESOLVED", "REJECTED")],
        "modules": {
            "telemetry":    "ONLINE" if tel else "OFFLINE",
            "maintenance":  "ONLINE" if pred else "WARMING_UP",
            "energy":       "ONLINE" if energy else "WARMING_UP",
            "safety":       "ONLINE" if safety else "WARMING_UP",
            "security":     "PROTECTED" if sec.security_status == "PROTECTED" else "ELEVATED",
            "ai":           "AVAILABLE",
        },
    }

    if risk_data["system_risk"] in ("HIGH", "CRITICAL"):
        logger.warning("🧠  System risk %s | Score=%.0f | Alerts=%d",
                       risk_data["system_risk"], risk_data["system_score"], active_alerts)

    return snapshot