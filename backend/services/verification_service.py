from backend.services.demo_controller import get_scenario


def verify_remediation(incident) -> dict:
    before = {"condition": "Elevated temperature and vibration", "scenario": incident.verification.get("before_scenario", "UNKNOWN")}
    after = {"condition": "Simulated load reduced; monitoring required", "scenario": get_scenario()}
    return {
        "verification_status": "VERIFIED",
        "before_state": before,
        "after_state": after,
        "improvement_detected": True,
        "explanation": "The safe simulated action completed and the incident is marked improved for demonstration. Live equipment was not controlled.",
    }