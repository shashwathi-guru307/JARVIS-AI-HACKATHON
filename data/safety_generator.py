import random
from datetime import datetime, timezone
from backend.utils.config import get_demo_scenario

DEVICE_ID = "MACHINE_01"

_session_start = datetime.now(timezone.utc)
_last_activity = datetime.now(timezone.utc)


def generate_safety() -> dict:
    global _last_activity

    scenario = get_demo_scenario()

    profiles = {
        "normal":               {"present": True,  "activity": 0.75, "inactivity": 0,    "env_risk": "NORMAL", "prox": "SAFE",   "fatigue": "NONE",     "emergency": "NONE"},
        "inactive":             {"present": True,  "activity": 0.05, "inactivity": 480,  "env_risk": "NORMAL", "prox": "SAFE",   "fatigue": "POSSIBLE", "emergency": "NONE"},
        "environmental_warning":{"present": True,  "activity": 0.60, "inactivity": 0,    "env_risk": "HIGH",   "prox": "SAFE",   "fatigue": "NONE",     "emergency": "NONE"},
        "proximity_warning":    {"present": True,  "activity": 0.70, "inactivity": 0,    "env_risk": "MEDIUM", "prox": "HIGH",   "fatigue": "NONE",     "emergency": "NONE"},
        "fatigue_pattern":      {"present": True,  "activity": 0.15, "inactivity": 720,  "env_risk": "LOW",    "prox": "SAFE",   "fatigue": "HIGH",     "emergency": "NONE"},
        "emergency":            {"present": True,  "activity": 0.0,  "inactivity": 900,  "env_risk": "CRITICAL","prox":"CRITICAL","fatigue": "HIGH",     "emergency": "MANUAL_SOS"},
        "degrading":            {"present": True,  "activity": 0.55, "inactivity": 60,   "env_risk": "MEDIUM", "prox": "MEDIUM", "fatigue": "NONE",     "emergency": "NONE"},
        "high_risk":            {"present": True,  "activity": 0.40, "inactivity": 180,  "env_risk": "HIGH",   "prox": "HIGH",   "fatigue": "POSSIBLE", "emergency": "NONE"},
        "critical":             {"present": True,  "activity": 0.10, "inactivity": 600,  "env_risk": "CRITICAL","prox":"CRITICAL","fatigue": "HIGH",     "emergency": "NONE"},
    }

    p = profiles.get(scenario, profiles["normal"])

    activity_level = round(max(0.0, min(1.0, p["activity"] + random.uniform(-0.05, 0.05))), 3)
    inactivity_sec = round(max(0.0, p["inactivity"] + random.uniform(-10, 10)), 1)

    return {
        "device_id":                 DEVICE_ID,
        "timestamp":                 datetime.now(timezone.utc).isoformat(),
        "operator_present":          p["present"],
        "activity_level":            activity_level,
        "inactivity_duration_seconds": inactivity_sec,
        "environmental_risk":        p["env_risk"],
        "fatigue_indicator":         p["fatigue"],
        "proximity_risk":            p["prox"],
        "emergency_status":          p["emergency"],
    }