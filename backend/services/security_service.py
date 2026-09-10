import logging
import uuid
from collections import deque
from datetime import datetime, timezone

from backend.models.security_models import SecurityEvent, SecurityStatus
from backend.services.audit_service import log_event
from backend.services.transaction_risk_service import get_transaction_risks

logger = logging.getLogger(__name__)

MAX_SECURITY_EVENTS = 200
_events: deque = deque(maxlen=MAX_SECURITY_EVENTS)
_auth_failures = 0
_api_spike_count = 0

RISK_ORDER = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def _max_risk(*risks: str) -> str:
    return max(risks, key=lambda r: RISK_ORDER.index(r) if r in RISK_ORDER else 0)


def _risk_to_score(risk: str) -> float:
    return {"LOW": 15.0, "MEDIUM": 40.0, "HIGH": 70.0, "CRITICAL": 90.0}.get(risk, 10.0)


def emit_event(event_type: str, severity: str, source: str, description: str,
               risk_score: float, action: str) -> SecurityEvent:
    event = SecurityEvent(
        event_id=str(uuid.uuid4())[:8].upper(),
        timestamp=datetime.now(timezone.utc),
        event_type=event_type,
        severity=severity,
        source=source,
        description=description,
        risk_score=risk_score,
        recommended_action=action,
    )
    _events.appendleft(event)
    log_event(event_type, source, severity, description)
    if severity in ("HIGH", "CRITICAL"):
        logger.warning("🔐  Security [%s] %s: %s", severity, event_type, description)
    return event


def record_auth_failure(username: str) -> None:
    global _auth_failures
    _auth_failures += 1
    severity = "HIGH" if _auth_failures >= 3 else "MEDIUM"
    emit_event(
        "AUTHENTICATION_FAILURE", severity, username,
        f"Authentication failure #{_auth_failures} for user: {username}",
        _risk_to_score(severity),
        "Review access activity and verify that login attempts are legitimate.",
    )


def record_auth_success(username: str) -> None:
    global _auth_failures
    _auth_failures = 0
    log_event("AUTHENTICATION_SUCCESS", username, "LOW", f"Successful login: {username}")


def record_rate_limit(source: str) -> None:
    emit_event(
        "RATE_LIMIT", "MEDIUM", source,
        f"Rate limit triggered for: {source}",
        35.0,
        "Review the request source and verify that the activity is legitimate.",
    )


def record_api_spike(source: str, count: int) -> None:
    emit_event(
        "SUSPICIOUS_API_ACTIVITY", "HIGH", source,
        f"Unusual API activity: {count} requests in a short window",
        60.0,
        "Review the source activity and verify that the request pattern is legitimate.",
    )


def get_security_status() -> SecurityStatus:
    transaction_risks  = get_transaction_risks(20)
    tx_risk            = max((r.risk_level for r in transaction_risks), key=lambda r: RISK_ORDER.index(r) if r in RISK_ORDER else 0) if transaction_risks else "LOW"
    auth_risk          = "HIGH" if _auth_failures >= 3 else ("MEDIUM" if _auth_failures >= 1 else "LOW")
    recent_events      = list(_events)[:20]
    event_risk         = max((e.severity for e in recent_events), key=lambda r: RISK_ORDER.index(r) if r in RISK_ORDER else 0) if recent_events else "LOW"
    overall_risk       = _max_risk(tx_risk, auth_risk, event_risk)
    active_alerts      = sum(1 for e in recent_events if e.severity in ("HIGH", "CRITICAL"))
    risk_score         = _risk_to_score(overall_risk)

    security_status    = (
        "COMPROMISED" if overall_risk == "CRITICAL" else
        "ELEVATED"    if overall_risk in ("HIGH", "MEDIUM") else
        "PROTECTED"
    )

    return SecurityStatus(
        security_status=security_status,
        authentication="ACTIVE",
        authorization="ACTIVE",
        rate_limiting="ACTIVE",
        audit_logging="ACTIVE",
        active_alerts=active_alerts,
        risk_level=overall_risk,
        risk_score=risk_score,
    )


def get_security_events(limit: int = 50) -> list[SecurityEvent]:
    return list(_events)[:limit]