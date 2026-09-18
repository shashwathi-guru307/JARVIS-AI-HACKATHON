from fastapi import APIRouter

from backend.services.demo_controller import get_scenario, get_telemetry_overrides

router = APIRouter(prefix="/manufacturing", tags=["Smart Manufacturing"])


@router.get("/plant")
def manufacturing_plant():
    return {
        "plant": "Smart Manufacturing Plant",
        "production_line": "Assembly Line A",
        "machine": {
            "machine_id": "M-101",
            "name": "M-101",
            "type": "Industrial rotating production machine",
            "criticality": "HIGH",
            "operational_status": "RECOVERY_SIMULATION" if get_scenario() == "RECOVERY" else "MONITORED",
        },
        "scenario": get_scenario(),
        "telemetry": get_telemetry_overrides(),
        "thresholds": {
            "temperature_warning_c": 85,
            "temperature_critical_c": 95,
            "vibration_warning": 0.60,
            "vibration_critical": 0.90,
            "battery_warning_percent": 30,
            "battery_critical_percent": 10,
            "note": "Configurable demo thresholds, not universal industrial standards.",
        },
    }