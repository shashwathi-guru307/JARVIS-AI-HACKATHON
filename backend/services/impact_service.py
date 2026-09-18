def assess_impact(incident) -> dict:
    high_risk = incident.severity in ("HIGH", "CRITICAL")
    return {
        "affected_area": "Production machine",
        "operational_impact": "Potential production interruption" if high_risk else "Reduced operating margin",
        "potential_downtime": "Possible unplanned downtime" if high_risk else "Maintenance window may be required",
        "safety_impact": "Elevated operational safety concern" if high_risk else "Monitor operating conditions",
        "financial_impact_category": "HIGH" if high_risk else "MEDIUM",
        "urgency": "HIGH" if high_risk else "MEDIUM",
        "explanation": "Temperature, vibration, and maintenance indicators are correlated; continued operation could increase mechanical stress.",
    }