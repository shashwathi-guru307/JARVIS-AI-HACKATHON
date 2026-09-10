# telemetry_storage.py — lightweight in-memory telemetry history
# Easy to replace with MongoDB/PostgreSQL later — only this file changes.
import logging
from collections import deque
from datetime import datetime
from backend.models.telemetry_models import TelemetryData
from backend.utils.config import get_telemetry_history_limit

logger = logging.getLogger(__name__)

# One deque per device_id
_history: dict[str, deque] = {}


def _get_deque(device_id: str) -> deque:
    limit = get_telemetry_history_limit()
    if device_id not in _history:
        _history[device_id] = deque(maxlen=limit)
    return _history[device_id]


def save_telemetry(data: TelemetryData) -> None:
    """Append one validated TelemetryData reading to the device's history."""
    dq = _get_deque(data.device_id)
    dq.append(data)


def get_recent_telemetry(device_id: str, n: int = 100) -> list[TelemetryData]:
    """Return the n most recent readings for a device (oldest first)."""
    dq = _get_deque(device_id)
    items = list(dq)
    return items[-n:] if len(items) >= n else items


def get_latest_telemetry(device_id: str) -> TelemetryData | None:
    dq = _get_deque(device_id)
    return dq[-1] if dq else None


def get_device_history(device_id: str) -> list[TelemetryData]:
    return list(_get_deque(device_id))


def history_length(device_id: str) -> int:
    return len(_get_deque(device_id))