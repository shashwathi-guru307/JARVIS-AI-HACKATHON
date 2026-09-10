# predictive_model.py — loads the trained model and exposes predict()
import logging
from pathlib import Path
import joblib
import numpy as np

logger = logging.getLogger(__name__)

MODEL_PATH = (
    Path(__file__).resolve().parent
    / "models"
    / "predictive_maintenance.joblib"
)

# 0=healthy 1=degrading 2=high_risk 3=critical
_LABEL_MAP = {
    0: ("STABLE",    "LOW"),
    1: ("DEGRADING", "MEDIUM"),
    2: ("HIGH_RISK", "HIGH"),
    3: ("CRITICAL",  "CRITICAL"),
}

_artifact = None


def _load() -> bool:
    global _artifact
    if _artifact is not None:
        return True
    if not MODEL_PATH.exists():
        logger.warning("Predictive model not found at %s — using rule-based fallback", MODEL_PATH)
        return False
    try:
        _artifact = joblib.load(MODEL_PATH)
        logger.info("Predictive model loaded from %s", MODEL_PATH)
        return True
    except Exception as exc:
        logger.error("Model load error: %s", exc)
        return False


def predict(features: dict) -> dict:
    """
    Run ML prediction (or rule-based fallback).

    Returns:
        degradation_status  str
        risk_level          str
        failure_risk        float  0–1
        label               int
        ml_used             bool
    """
    if _load() and _artifact:
        feat_names = _artifact["features"]
        X = np.array([[features.get(f, 0.0) for f in feat_names]])
        clf   = _artifact["model"]
        label = int(clf.predict(X)[0])
        proba = clf.predict_proba(X)[0]
        failure_risk = float(proba[2] + proba[3])   # prob of high_risk + critical
        deg_status, risk_level = _LABEL_MAP[label]
        return {
            "degradation_status": deg_status,
            "risk_level": risk_level,
            "failure_risk": round(failure_risk, 3),
            "label": label,
            "ml_used": True,
        }

    # Rule-based fallback
    return _rule_based(features)


def _rule_based(features: dict) -> dict:
    """Deterministic fallback when the ML model is unavailable."""
    temp   = features.get("current_temperature", 72)
    vib    = features.get("current_vibration", 0.3)
    arate  = features.get("anomaly_rate", 0.0)
    tslope = features.get("temperature_slope", 0.0)

    score = 0
    if temp > 95:    score += 3
    elif temp > 85:  score += 1
    if vib > 0.9:    score += 3
    elif vib > 0.6:  score += 1
    if arate > 0.3:  score += 2
    if tslope > 0.1: score += 1

    if score >= 6:
        return {"degradation_status": "CRITICAL",  "risk_level": "CRITICAL", "failure_risk": 0.92, "label": 3, "ml_used": False}
    if score >= 4:
        return {"degradation_status": "HIGH_RISK", "risk_level": "HIGH",     "failure_risk": 0.71, "label": 2, "ml_used": False}
    if score >= 2:
        return {"degradation_status": "DEGRADING", "risk_level": "MEDIUM",   "failure_risk": 0.42, "label": 1, "ml_used": False}
    return         {"degradation_status": "STABLE",    "risk_level": "LOW",      "failure_risk": 0.12, "label": 0, "ml_used": False}