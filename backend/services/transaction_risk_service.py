import logging
from collections import deque
from datetime import datetime, timezone

from data.transaction_generator import generate_transaction
from backend.models.transaction_models import Transaction, TransactionRisk, TransactionSummary

logger = logging.getLogger(__name__)

MAX_TRANSACTION_HISTORY = 200
_transactions: deque = deque(maxlen=MAX_TRANSACTION_HISTORY)
_risk_history: deque = deque(maxlen=MAX_TRANSACTION_HISTORY)

AMOUNT_HIGH_THRESHOLD    = 10000.0
AMOUNT_CRITICAL_THRESHOLD= 50000.0
KNOWN_DEVICES = {"device_primary", "device_secondary"}
HOME_LOCATIONS = {"Mumbai", "Delhi"}


def _calculate_risk(tx: Transaction, recent: list[Transaction]) -> TransactionRisk:
    score = 0.0
    contributors = []

    # High amount
    if tx.amount >= AMOUNT_CRITICAL_THRESHOLD:
        score += 40
        contributors.append(f"Very high transaction amount: ₹{tx.amount:,.0f}")
    elif tx.amount >= AMOUNT_HIGH_THRESHOLD:
        score += 20
        contributors.append(f"High transaction amount: ₹{tx.amount:,.0f}")

    # Rapid transactions
    if tx.is_rapid and len(recent) >= 3:
        score += 25
        contributors.append(f"Rapid transaction pattern: {len(recent)} recent transactions")

    # New device
    if tx.device_id not in KNOWN_DEVICES:
        score += 20
        contributors.append(f"Unrecognised device: {tx.device_id}")

    # Unusual location
    if tx.location not in HOME_LOCATIONS:
        score += 15
        contributors.append(f"Unusual location: {tx.location}")

    score = min(score, 100.0)

    if score >= 75:   risk_level = "CRITICAL"
    elif score >= 50: risk_level = "HIGH"
    elif score >= 25: risk_level = "MEDIUM"
    else:             risk_level = "LOW"

    if risk_level in ("HIGH", "CRITICAL"):
        recommendation = "Verify the transaction activity before treating it as legitimate."
    elif risk_level == "MEDIUM":
        recommendation = "Monitor for additional unusual activity."
    else:
        recommendation = "Transaction appears normal. Continue monitoring."

    return TransactionRisk(
        transaction_id=tx.transaction_id,
        timestamp=tx.timestamp,
        risk_score=round(score, 1),
        risk_level=risk_level,
        contributors=contributors,
        recommendation=recommendation,
        is_suspicious=risk_level in ("HIGH", "CRITICAL"),
    )


def generate_and_assess_transaction() -> tuple[Transaction, TransactionRisk]:
    raw = generate_transaction()
    tx  = Transaction(**raw)

    recent = list(_transactions)[-10:]
    risk   = _calculate_risk(tx, recent)

    _transactions.append(tx)
    _risk_history.append(risk)

    if risk.is_suspicious:
        logger.warning("💳  Suspicious transaction %s | Risk=%s | Score=%.0f",
                       tx.transaction_id, risk.risk_level, risk.risk_score)
    else:
        logger.info("💳  Transaction %s | Risk=%s", tx.transaction_id, risk.risk_level)

    return tx, risk


def get_recent_transactions(n: int = 20) -> list[Transaction]:
    return list(_transactions)[-n:]


def get_transaction_risks(n: int = 20) -> list[TransactionRisk]:
    return list(_risk_history)[-n:]


def get_transaction_summary() -> TransactionSummary:
    risks = list(_risk_history)
    txs   = list(_transactions)

    high   = sum(1 for r in risks if r.risk_level in ("HIGH", "CRITICAL"))
    medium = sum(1 for r in risks if r.risk_level == "MEDIUM")
    low    = sum(1 for r in risks if r.risk_level == "LOW")

    amounts   = [t.amount for t in txs]
    total_amt = sum(amounts)
    avg_amt   = total_amt / len(amounts) if amounts else 0.0

    # Simple risk trend from last 20 vs previous 20
    if len(risks) >= 40:
        recent_avg  = sum(r.risk_score for r in risks[-20:]) / 20
        earlier_avg = sum(r.risk_score for r in risks[-40:-20]) / 20
        trend = "RISING" if recent_avg > earlier_avg + 5 else ("FALLING" if recent_avg < earlier_avg - 5 else "STABLE")
    else:
        trend = "STABLE"

    return TransactionSummary(
        total_count=len(txs),
        high_risk=high,
        medium_risk=medium,
        low_risk=low,
        total_amount=round(total_amt, 2),
        avg_amount=round(avg_amt, 2),
        risk_trend=trend,
    )