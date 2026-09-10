from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal


SOURCE_TYPES = Literal["TELEMETRY", "VISION", "MAINTENANCE", "ENERGY", "SAFETY", "SECURITY", "SYSTEM"]
SEVERITY_LEVELS = Literal["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]


class IntelligenceEvent(BaseModel):
    event_id: str
    timestamp: datetime
    source: SOURCE_TYPES
    event_type: str
    severity: SEVERITY_LEVELS
    risk_score: float = Field(..., ge=0.0, le=100.0)
    device_id: str | None = None
    title: str
    description: str
    contributing_factors: list[str] = []
    recommended_action: str
    status: Literal["ACTIVE", "ACKNOWLEDGED", "RESOLVED"] = "ACTIVE"
backend/services/risk_engine.py
"""
Unified Risk Engine — combines domain risk signals into one system-level risk score.
All calculations are deterministic and explainable.
"""
from backend.services.predictive_service import get_latest_prediction
from backend.services.energy_service import get_latest_metrics as get_latest_energy
from backend.services.safety_service import get_latest_safety
from backend.services.security_service import get_security_status
from backend.services.transaction_risk_service import get_transaction_risks

RISK_ORDER = ["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
RISK_SCORES = {"INFO": 5, "LOW": 15, "MEDIUM": 40, "HIGH": 70, "CRITICAL": 90}


def _level_to_score(level: str) -> float:
    return float(RISK_SCORES.get(level, 10))


def _score_to_level(score: float) -> str:
    if score >= 75: return "CRITICAL"
    if score >= 50: return "HIGH"
    if score >= 25: return "MEDIUM"
    return "LOW"


def _max_level(*levels: str) -> str:
    return max(levels, key=lambda r: RISK_ORDER.index(r) if r in RISK_ORDER else 0)


def calculate_system_risk() -> dict:
    """
    Collect the latest risk signal from every domain and combine into a
    weighted system risk score (0–100, higher = worse).

    Returns:
        system_risk     str     LOW / MEDIUM / HIGH / CRITICAL
        system_score    float   0–100 (inverted: higher = better system health)
        domain_risks    dict    per-domain risk levels
        contributing    list    human-readable factors driving the risk
        recommendation  str     most urgent action
    """
    domain_risks = {}
    contributing = []

    # Machine / predictive maintenance
    pred = get_latest_prediction()
    if pred:
        domain_risks["machine"] = pred.risk_level
        if pred.risk_level in ("HIGH", "CRITICAL"):
            contributing.append(f"Machine failure risk {pred.risk_level}: health {pred.health_score:.0f}/100")
    else:
        domain_risks["machine"] = "LOW"

    # Energy
    energy = get_latest_energy()
    if energy:
        eff = energy.efficiency_score
        if eff < 50:   e_risk = "HIGH"
        elif eff < 70: e_risk = "MEDIUM"
        else:           e_risk = "LOW"
        domain_risks["energy"] = e_risk
        if e_risk in ("HIGH", "MEDIUM"):
            contributing.append(f"Energy efficiency low: {eff:.0f}/100")
    else:
        domain_risks["energy"] = "LOW"

    # Safety
    safety = get_latest_safety()
    if safety:
        domain_risks["safety"] = safety.overall_risk
        if safety.overall_risk in ("HIGH", "CRITICAL"):
            contributing.append(f"Safety risk {safety.overall_risk}: score {safety.safety_score:.0f}/100")
    else:
        domain_risks["safety"] = "LOW"

    # Security
    sec = get_security_status()
    domain_risks["security"] = sec.risk_level
    if sec.risk_level in ("HIGH", "CRITICAL"):
        contributing.append(f"Security risk {sec.risk_level}: {sec.active_alerts} active alerts")

    # Transaction
    tx_risks = get_transaction_risks(10)
    if tx_risks:
        worst_tx = max(tx_risks, key=lambda r: _level_to_score(r.risk_level))
        domain_risks["transaction"] = worst_tx.risk_level
        if worst_tx.is_suspicious:
            contributing.append(f"Suspicious transaction pattern: risk {worst_tx.risk_level}")
    else:
        domain_risks["transaction"] = "LOW"

    # Weighted average (machine 30%, safety 25%, security 20%, transaction 15%, energy 10%)
    weights = {"machine": 0.30, "safety": 0.25, "security": 0.20, "transaction": 0.15, "energy": 0.10}
    raw_score = sum(_level_to_score(domain_risks.get(k, "LOW")) * w for k, w in weights.items())

    system_risk  = _score_to_level(raw_score)
    # System health score is inverse (higher = better)
    system_health = round(max(0.0, min(100.0, 100 - raw_score)), 1)

    # Overall recommendation
    overall_level = _max_level(*domain_risks.values())
    if overall_level == "CRITICAL":
        recommendation = "Critical conditions detected across multiple domains. Immediate review required."
    elif overall_level == "HIGH":
        recommendation = "Multiple elevated risk conditions. Prioritize review of high-risk domains."
    elif overall_level == "MEDIUM":
        recommendation = "Moderate risk conditions detected. Monitor closely and address contributing factors."
    else:
        recommendation = "System operating within normal parameters. Continue routine monitoring."

    return {
        "system_risk":    system_risk,
        "system_score":   system_health,
        "domain_risks":   domain_risks,
        "contributing":   contributing,
        "recommendation": recommendation,
    }