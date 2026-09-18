def prioritize_incident(severity: str, risk_score: float, alert_count: int, components: list[str], impact: dict) -> dict:
    score = min(100.0, risk_score + min(alert_count * 4, 16) + min(len(components) * 3, 12))
    if impact.get("urgency") == "HIGH":
        score = min(100.0, score + 10)
    if severity == "CRITICAL" or score >= 85:
        level = "CRITICAL"
    elif severity == "HIGH" or score >= 65:
        level = "HIGH"
    elif score >= 35:
        level = "MEDIUM"
    else:
        level = "LOW"
    return {
        "priority": level,
        "priority_score": round(score, 1),
        "explanation": f"Priority considers {alert_count} correlated alerts, {len(components)} affected components, risk {risk_score:.0f}, and {impact.get('urgency', 'MEDIUM')} urgency.",
    }