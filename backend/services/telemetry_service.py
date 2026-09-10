# telemetry_service.py — orchestrates generation, validation, and detection
import logging
from datetime import datetime
from data.generator import generate_telemetry
from backend.models.telemetry_models import TelemetryData, TelemetryEvent
from backend.services.anomaly_service import analyze_telemetry
from backend.services.telemetry_storage import save_telemetry   # ← Day 5 addition

logger = logging.getLogger(__name__)

_latest_event: TelemetryEvent | None = None


def get_latest_event() -> TelemetryEvent | None:
    return _latest_event


def generate_and_analyze() -> TelemetryEvent:
    global _latest_event

    raw  = generate_telemetry()
    data = TelemetryData(**raw)

    save_telemetry(data)          # ← Day 5: persist to rolling history

    analysis = analyze_telemetry(data)

    if analysis.status != "NORMAL":
        for reason in analysis.reasons:
            logger.warning("⚠  %s | %s", data.device_id, reason)
    else:
        logger.info("✅  %s | NORMAL", data.device_id)

    event = TelemetryEvent(
        device_id=data.device_id,
        timestamp=data.timestamp,
        telemetry={
            "temperature": data.temperature,
            "humidity":    data.humidity,
            "pressure":    data.pressure,
            "vibration":   data.vibration,
            "rpm":         data.rpm,
            "battery":     data.battery,
        },
        analysis=analysis,
    )

    _latest_event = event
    return event