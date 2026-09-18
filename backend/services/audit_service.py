import logging
import uuid
from collections import deque
from datetime import datetime, timezone
from backend.models.security_models import AuditEntry

logger = logging.getLogger(__name__)

MAX_AUDIT_ENTRIES = 500
_audit_log: deque = deque(maxlen=MAX_AUDIT_ENTRIES)


def log_event(event_type: str, user_id: str, severity: str, description: str) -> str:
    """Append one audit entry. Never log passwords, secrets, or tokens."""
    audit_id = str(uuid.uuid4())
    entry = AuditEntry(
        audit_id=audit_id,
        timestamp=datetime.now(timezone.utc),
        event_type=event_type,
        user_id=user_id,
        severity=severity,
        description=description,
    )
    _audit_log.appendleft(entry)

    if severity in ("HIGH", "CRITICAL"):
        logger.warning("🔒  AUDIT [%s] %s: %s", severity, event_type, description)
    else:
        logger.info("🔒  AUDIT [%s] %s: %s", severity, event_type, description)
    return audit_id


def get_audit_log(limit: int = 100) -> list[AuditEntry]:
    return list(_audit_log)[:limit]