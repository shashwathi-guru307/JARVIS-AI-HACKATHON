# config.py — loads and validates environment variables at startup
import os
from dotenv import load_dotenv

load_dotenv()


def get_api_key() -> str:
    key = os.getenv("AI_API_KEY", "")
    if not key or key == "your_openai_api_key_here":
        raise ValueError("AI_API_KEY is not configured in your .env file.")
    return key


def get_model() -> str:
    return os.getenv("AI_MODEL", "gpt-4o")


def get_vision_mode() -> str:
    return os.getenv("VISION_MODE", "local").lower()


def get_vision_interval() -> int:
    try:
        return int(os.getenv("VISION_INTERVAL", "2"))
    except ValueError:
        return 2


def get_prediction_enabled() -> bool:
    return os.getenv("PREDICTION_ENABLED", "true").lower() == "true"


def get_prediction_interval() -> int:
    try:
        return int(os.getenv("PREDICTION_INTERVAL", "5"))
    except ValueError:
        return 5


def get_telemetry_history_limit() -> int:
    try:
        return int(os.getenv("TELEMETRY_HISTORY_LIMIT", "1000"))
    except ValueError:
        return 1000


def get_demo_scenario() -> str:
    """
    Controls the synthetic degradation scenario injected by the generator.
    Options: normal | degrading | high_risk | critical
    """
    return os.getenv("DEMO_SCENARIO", "normal").lower()
def get_jwt_secret() -> str:
    return os.getenv("JWT_SECRET", "change-this-to-a-random-secret-in-production")

def get_jwt_expiration_minutes() -> int:
    try:
        return int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))
    except ValueError:
        return 60

def get_rate_limit_requests() -> int:
    try:
        return int(os.getenv("RATE_LIMIT_REQUESTS", "30"))
    except ValueError:
        return 30

def get_demo_mode() -> bool:
    return os.getenv("DEMO_MODE", "true").lower() == "true"

"""
Centralized J.A.R.V.I.S. configuration.
All environment-driven settings live here.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Demo / Live mode ──────────────────────────────────────────────────────────
DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() == "true"
DEMO_SCENARIO: str = os.getenv("DEMO_SCENARIO", "NORMAL")  # see SCENARIO list below

# ── Intelligence toggles ──────────────────────────────────────────────────────
AI_ENABLED: bool     = os.getenv("AI_ENABLED", "true").lower() == "true"
VISION_ENABLED: bool = os.getenv("VISION_ENABLED", "true").lower() == "true"

# ── History limits ────────────────────────────────────────────────────────────
EVENT_HISTORY_LIMIT: int = int(os.getenv("EVENT_HISTORY_LIMIT", "200"))
ALERT_HISTORY_LIMIT: int = int(os.getenv("ALERT_HISTORY_LIMIT", "50"))
TELEMETRY_HISTORY:   int = int(os.getenv("TELEMETRY_HISTORY",   "60"))

# ── System update interval (seconds) ─────────────────────────────────────────
SYSTEM_UPDATE_INTERVAL: int = int(os.getenv("SYSTEM_UPDATE_INTERVAL", "5"))

# ── Auth ──────────────────────────────────────────────────────────────────────
JWT_SECRET:              str = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_EXPIRATION_MINUTES:  int = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))

# ── Rate limiting ─────────────────────────────────────────────────────────────
RATE_LIMIT_REQUESTS:      int = int(os.getenv("RATE_LIMIT_REQUESTS",      "60"))
RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))

# ── Valid demo scenarios ──────────────────────────────────────────────────────
VALID_SCENARIOS = {
    "NORMAL",
    "MACHINE_DEGRADATION",
    "ENERGY_PEAK",
    "SAFETY_WARNING",
    "SECURITY_INCIDENT",
    "MULTI_RISK",
    "FULL_CRISIS",
    "RECOVERY",
}