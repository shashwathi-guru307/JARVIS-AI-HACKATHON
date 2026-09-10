from backend.models.telemetry_models import (
    TelemetryResponse,
    TelemetryValues,
    AnomalyAnalysis,
)


response = TelemetryResponse(
    device_id="MACHINE_01",
    timestamp="2026-09-02T10:01:04",

    telemetry=TelemetryValues(
        temperature=96.2,
        humidity=47.1,
        pressure=101.2,
        vibration=0.94,
        rpm=2280,
        battery=89.4,
    ),

    analysis=AnomalyAnalysis(
        status="CRITICAL",
        risk_level="CRITICAL",
        reasons=[
            "Temperature exceeds critical threshold",
            "Vibration exceeds critical threshold",
        ],
    ),
)


print(response.model_dump_json(indent=4))