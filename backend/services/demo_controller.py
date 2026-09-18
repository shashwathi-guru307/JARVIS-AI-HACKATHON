"""
Centralized Demo Controller.
All scenario state lives here — never scattered across individual services.
"""
import logging
from backend.utils.config import DEMO_MODE, DEMO_SCENARIO, VALID_SCENARIOS

logger = logging.getLogger(__name__)

_current_scenario: str = DEMO_SCENARIO if DEMO_SCENARIO in VALID_SCENARIOS else "NORMAL"


def get_scenario() -> str:
    return _current_scenario


def set_scenario(scenario: str) -> str:
    global _current_scenario
    scenario = scenario.upper()
    if scenario not in VALID_SCENARIOS:
        raise ValueError(f"Unknown scenario '{scenario}'. Valid: {VALID_SCENARIOS}")
    _current_scenario = scenario
    if scenario in ("AI01_MACHINE_INCIDENT", "RECOVERY"):
        from datetime import datetime, timezone
        from backend.models.telemetry_models import TelemetryData
        from backend.services.predictive_service import run_prediction
        from backend.services.telemetry_storage import save_telemetry

        save_telemetry(TelemetryData(
            device_id="MACHINE_01", timestamp=datetime.now(timezone.utc),
            **SCENARIO_TELEMETRY[scenario],
        ))
        run_prediction()
    logger.info("🎬  Demo scenario → %s", scenario)
    return _current_scenario


def is_demo() -> bool:
    return DEMO_MODE


# ── Per-scenario overrides ────────────────────────────────────────────────────
# These dicts are read by the individual services to inject deterministic values.

SCENARIO_TELEMETRY: dict[str, dict] = {
    "NORMAL": {
        "temperature": 62.0, "vibration": 0.25, "rpm": 1450.0,
        "battery": 88.0, "humidity": 45.0, "pressure": 1013.0,
    },
    "MACHINE_DEGRADATION": {
        "temperature": 94.0, "vibration": 0.85, "rpm": 2300.0,
        "battery": 71.0, "humidity": 52.0, "pressure": 1010.0,
    },
    "AI01_MACHINE_INCIDENT": {
        "temperature": 94.0, "vibration": 0.85, "rpm": 2300.0,
        "battery": 71.0, "humidity": 52.0, "pressure": 1010.0,
    },
    "ENERGY_PEAK": {
        "temperature": 74.0, "vibration": 0.40, "rpm": 1800.0,
        "battery": 60.0, "humidity": 48.0, "pressure": 1011.0,
    },
    "SAFETY_WARNING": {
        "temperature": 88.0, "vibration": 0.75, "rpm": 2100.0,
        "battery": 65.0, "humidity": 55.0, "pressure": 1009.0,
    },
    "SECURITY_INCIDENT": {
        "temperature": 65.0, "vibration": 0.30, "rpm": 1500.0,
        "battery": 85.0, "humidity": 44.0, "pressure": 1013.0,
    },
    "MULTI_RISK": {
        "temperature": 96.0, "vibration": 0.92, "rpm": 2350.0,
        "battery": 58.0, "humidity": 57.0, "pressure": 1007.0,
    },
    "FULL_CRISIS": {
        "temperature": 102.0, "vibration": 1.05, "rpm": 2600.0,
        "battery": 42.0, "humidity": 62.0, "pressure": 1005.0,
    },
    "RECOVERY": {
        "temperature": 70.0, "vibration": 0.35, "rpm": 1550.0,
        "battery": 80.0, "humidity": 47.0, "pressure": 1012.0,
    },
}

SCENARIO_FLAGS: dict[str, dict] = {
    "NORMAL":             {"security_incident": False, "operator_proximity": False, "energy_peak": False},
    "MACHINE_DEGRADATION":{"security_incident": False, "operator_proximity": False, "energy_peak": False},
    "AI01_MACHINE_INCIDENT":{"security_incident": False, "operator_proximity": False, "energy_peak": False},
    "ENERGY_PEAK":        {"security_incident": False, "operator_proximity": False, "energy_peak": True},
    "SAFETY_WARNING":     {"security_incident": False, "operator_proximity": True,  "energy_peak": False},
    "SECURITY_INCIDENT":  {"security_incident": True,  "operator_proximity": False, "energy_peak": False},
    "MULTI_RISK":         {"security_incident": True,  "operator_proximity": True,  "energy_peak": True},
    "FULL_CRISIS":        {"security_incident": True,  "operator_proximity": True,  "energy_peak": True},
    "RECOVERY":           {"security_incident": False, "operator_proximity": False, "energy_peak": False},
}


def get_telemetry_overrides() -> dict:
    return SCENARIO_TELEMETRY.get(_current_scenario, SCENARIO_TELEMETRY["NORMAL"])


def get_flags() -> dict:
    return SCENARIO_FLAGS.get(_current_scenario, SCENARIO_FLAGS["NORMAL"])