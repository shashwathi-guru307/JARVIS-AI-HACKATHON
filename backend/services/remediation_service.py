from backend.models.incident_models import RemediationStep


def generate_remediation_plan(incident) -> list[RemediationStep]:
    return [RemediationStep(
        action_id=f"SIM-{incident.incident_id[-8:]}",
        description="Reduce simulated machine load",
        reason="High temperature and vibration indicate elevated mechanical stress.",
        expected_effect="Reduce simulated operational stress while maintenance review is performed.",
        risk_level="LOW",
        approval_required=True,
        safe_to_simulate=True,
    )]