from pydantic import ValidationError

from backend.models.telemetry_models import TelemetryData


valid_data = {
    "device_id": "MACHINE_01",
    "timestamp": "2026-09-02T10:00:00",
    "temperature": 72.4,
    "humidity": 48.2,
    "pressure": 101.3,
    "vibration": 0.32,
    "rpm": 1820,
    "battery": 91.5
}


try:
    telemetry = TelemetryData(**valid_data)

    print("✅ Telemetry is valid")
    print(telemetry)

except ValidationError as e:
    print("❌ Telemetry is invalid")
    print(e)