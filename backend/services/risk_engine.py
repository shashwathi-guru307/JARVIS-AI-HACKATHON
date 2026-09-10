"""
J.A.R.V.I.S. System Risk Engine

Combines risk signals from:
- Predictive maintenance
- Energy intelligence
- Human safety
- Security
- Transaction monitoring
- Telemetry

Produces one explainable system-level risk result.
"""

import logging

from backend.services.predictive_service import get_latest_prediction
from backend.services.energy_service import get_latest_metrics
from backend.services.safety_service import get_latest_safety
from backend.services.security_service import get_security_status
from backend.services.transaction_risk_service import get_transaction_summary
from backend.services.telemetry_storage import get_latest_telemetry


logger = logging.getLogger(__name__)

DEVICE_ID = "MACHINE_01"


# ============================================================
# RISK LEVEL HELPERS
# ============================================================

def _level_to_score(level: str | None) -> int:
    """
    Convert a risk level into a numeric score.

    LOW       = 0
    MEDIUM     = 40
    HIGH       = 70
    CRITICAL   = 100
    """

    return {
        "LOW": 0,
        "MEDIUM": 40,
        "HIGH": 70,
        "CRITICAL": 100,
    }.get((level or "LOW").upper(), 0)


def _score_to_level(score: float) -> str:
    """
    Convert a numeric risk score into a risk level.
    """

    if score >= 80:
        return "CRITICAL"

    if score >= 60:
        return "HIGH"

    if score >= 35:
        return "MEDIUM"

    return "LOW"


def _max_level(*levels: str | None) -> str:
    """
    Return the highest risk level from the supplied levels.
    """

    priority = {
        "LOW": 0,
        "MEDIUM": 1,
        "HIGH": 2,
        "CRITICAL": 3,
    }

    valid_levels = [
        (level or "LOW").upper()
        for level in levels
    ]

    if not valid_levels:
        return "LOW"

    return max(
        valid_levels,
        key=lambda level: priority.get(level, 0),
    )


# ============================================================
# BACKWARD-COMPATIBILITY HELPERS
# ============================================================

def _risk_value(level: str | None) -> int:
    """
    Backward-compatible alias for older code.
    """
    return {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
        "CRITICAL": 4,
    }.get((level or "LOW").upper(), 1)


def _overall_risk(score: float) -> str:
    """
    Backward-compatible alias for score-to-level conversion.
    """
    return _score_to_level(score)


def get_latest_energy():
    """
    Compatibility wrapper used by the risk-engine tests.

    Internally this uses the existing energy service function.
    """
    return get_latest_metrics()


def get_transaction_risks():
    """
    Compatibility wrapper used by the risk-engine tests.

    The current transaction service exposes a summary rather than
    a transaction-risk list, so return that existing summary object.
    Tests can mock this function with a list when required.
    """
    return get_transaction_summary()


# ============================================================
# SYSTEM RISK CALCULATION
# ============================================================

def calculate_system_risk() -> dict:
    """
    Collect the latest available signals from every intelligence
    domain and calculate one unified, explainable system risk.
    """

    # ---------------------------------------------------------
    # Collect latest intelligence
    # ---------------------------------------------------------

    prediction = get_latest_prediction()

    # Use compatibility function so tests can mock it.
    energy = get_latest_energy()

    safety = get_latest_safety()

    security = get_security_status()

    # Use compatibility function so tests can mock it.
    transactions = get_transaction_risks()

    telemetry = get_latest_telemetry(DEVICE_ID)

    # ---------------------------------------------------------
    # Default domain risk levels
    # ---------------------------------------------------------

    domain_risks = {
        "maintenance": "LOW",
        "energy": "LOW",
        "safety": "LOW",
        "security": "LOW",
        "transactions": "LOW",
        "telemetry": "LOW",
    }

    contributing = []

    # =========================================================
    # 1. PREDICTIVE MAINTENANCE
    # =========================================================

    if prediction:
        maintenance_risk = (
            getattr(prediction, "risk_level", "LOW") or "LOW"
        ).upper()

        domain_risks["maintenance"] = maintenance_risk

        if maintenance_risk in ("HIGH", "CRITICAL"):
            contributing.append(
                f"Predictive maintenance risk is {maintenance_risk}"
            )

    # =========================================================
    # 2. ENERGY INTELLIGENCE
    # =========================================================

    if energy:
        efficiency = getattr(
            energy,
            "efficiency_score",
            None,
        )

        if efficiency is not None:

            if efficiency < 40:
                energy_risk = "CRITICAL"

            elif efficiency < 60:
                energy_risk = "HIGH"

            elif efficiency < 75:
                energy_risk = "MEDIUM"

            else:
                energy_risk = "LOW"

            domain_risks["energy"] = energy_risk

            if energy_risk in ("HIGH", "CRITICAL"):
                contributing.append(
                    f"Energy efficiency is low at {efficiency:.0f}%"
                )

    # =========================================================
    # 3. HUMAN SAFETY
    # =========================================================

    if safety:
        safety_risk = (
            getattr(safety, "overall_risk", "LOW") or "LOW"
        ).upper()

        domain_risks["safety"] = safety_risk

        if safety_risk in ("HIGH", "CRITICAL"):
            contributing.append(
                f"Human safety risk is {safety_risk}"
            )

    # =========================================================
    # 4. SECURITY
    # =========================================================

    if security:
        security_risk = (
            getattr(security, "risk_level", "LOW") or "LOW"
        ).upper()

        domain_risks["security"] = security_risk

        if security_risk in ("HIGH", "CRITICAL"):
            contributing.append(
                f"Security risk is {security_risk}"
            )

    # =========================================================
    # 5. TRANSACTION MONITORING
    # =========================================================

    if transactions:

        # -----------------------------------------------------
        # Case A: transaction summary object
        # -----------------------------------------------------

        if hasattr(transactions, "high_risk"):

            high_risk = getattr(
                transactions,
                "high_risk",
                0,
            )

            medium_risk = getattr(
                transactions,
                "medium_risk",
                0,
            )

            if high_risk > 0:
                transaction_risk = "HIGH"

                contributing.append(
                    f"{high_risk} high-risk transaction(s) detected"
                )

            elif medium_risk > 0:
                transaction_risk = "MEDIUM"

            else:
                transaction_risk = "LOW"

            domain_risks["transactions"] = transaction_risk

        # -----------------------------------------------------
        # Case B: transaction risk list
        # -----------------------------------------------------

        elif isinstance(transactions, list):

            high_count = 0
            medium_count = 0

            for transaction in transactions:

                if isinstance(transaction, dict):
                    risk_level = transaction.get(
                        "risk_level",
                        "LOW",
                    )

                else:
                    risk_level = getattr(
                        transaction,
                        "risk_level",
                        "LOW",
                    )

                risk_level = (
                    risk_level or "LOW"
                ).upper()

                if risk_level == "HIGH" or risk_level == "CRITICAL":
                    high_count += 1

                elif risk_level == "MEDIUM":
                    medium_count += 1

            if high_count > 0:
                domain_risks["transactions"] = "HIGH"

                contributing.append(
                    f"{high_count} high-risk transaction(s) detected"
                )

            elif medium_count > 0:
                domain_risks["transactions"] = "MEDIUM"

    # =========================================================
    # 6. RAW TELEMETRY
    # =========================================================

    if telemetry:

        telemetry_score = 0

        temperature = getattr(
            telemetry,
            "temperature",
            0,
        )

        vibration = getattr(
            telemetry,
            "vibration",
            0,
        )

        battery = getattr(
            telemetry,
            "battery",
            100,
        )

        # -----------------------------------------------------
        # Temperature
        # -----------------------------------------------------

        if temperature > 95:

            telemetry_score += 45

            contributing.append(
                f"Critical temperature detected: "
                f"{temperature:.1f}°C"
            )

        elif temperature > 85:

            telemetry_score += 25

            contributing.append(
                f"Elevated temperature detected: "
                f"{temperature:.1f}°C"
            )

        # -----------------------------------------------------
        # Vibration
        # -----------------------------------------------------

        if vibration > 0.9:

            telemetry_score += 45

            contributing.append(
                f"Critical vibration detected: "
                f"{vibration:.2f}g"
            )

        elif vibration > 0.6:

            telemetry_score += 25

            contributing.append(
                f"Elevated vibration detected: "
                f"{vibration:.2f}g"
            )

        # -----------------------------------------------------
        # Battery
        # -----------------------------------------------------

        if battery < 10:

            telemetry_score += 30

            contributing.append(
                f"Critical battery level: "
                f"{battery:.0f}%"
            )

        elif battery < 30:

            telemetry_score += 15

        # -----------------------------------------------------
        # Convert telemetry score to risk
        # -----------------------------------------------------

        telemetry_risk = _score_to_level(
            telemetry_score
        )

        domain_risks["telemetry"] = telemetry_risk

    # =========================================================
    # WEIGHTED SYSTEM SCORE
    # =========================================================

    weights = {
        "maintenance": 0.25,
        "safety": 0.25,
        "security": 0.15,
        "energy": 0.10,
        "transactions": 0.10,
        "telemetry": 0.15,
    }

    score = 0.0

    for domain, weight in weights.items():

        level = domain_risks[domain]

        level_score = _level_to_score(level)

        score += level_score * weight

    score = round(score, 1)

    system_risk = _score_to_level(score)

        # ---------------------------------------------------------
    # High/Critical domain escalation
    # ---------------------------------------------------------
    # A critical condition in any major intelligence domain
    # should not be hidden by weighted averaging.

    if any(
        domain_risks[domain] == "CRITICAL"
        for domain in domain_risks
    ):
        system_risk = "CRITICAL"
        score = max(score, 80.0)

    elif any(
        domain_risks[domain] == "HIGH"
        for domain in domain_risks
    ):
        system_risk = _max_level(
            system_risk,
            "HIGH",
        )

    # =========================================================
    # SAFETY OVERRIDE
    # =========================================================

    if domain_risks["safety"] == "CRITICAL":

        system_risk = "CRITICAL"

        score = max(
            score,
            80.0,
        )

    # =========================================================
    # RECOMMENDATION
    # =========================================================

    if system_risk == "CRITICAL":

        recommendation = (
            "Immediate intervention required. "
            "Stop or isolate affected operations where safe "
            "and investigate the highest-risk conditions."
        )

    elif system_risk == "HIGH":

        recommendation = (
            "Urgent review required. Prioritize maintenance, "
            "safety, security, and operational conditions "
            "contributing to the risk."
        )

    elif system_risk == "MEDIUM":

        recommendation = (
            "Review elevated conditions and continue enhanced "
            "monitoring. Schedule corrective action where appropriate."
        )

    else:

        recommendation = (
            "System operating within acceptable conditions. "
            "Continue normal monitoring."
        )

    # =========================================================
    # LOGGING
    # =========================================================

    logger.info(
        "System risk calculated: %s | Score=%.1f | Domains=%s",
        system_risk,
        score,
        domain_risks,
    )

    # =========================================================
    # FINAL RESULT
    # =========================================================

    return {
        "system_risk": system_risk,
        "system_score": score,
        "domain_risks": domain_risks,
        "contributing": contributing,
        "recommendation": recommendation,
    }