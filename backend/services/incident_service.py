import uuid
from datetime import datetime, timezone

from backend.models.incident_models import Incident
from backend.services.audit_service import log_event
from backend.services.correlation_service import get_correlated_event_groups
from backend.services.incident_priority_service import prioritize_incident
from backend.services.impact_service import assess_impact
from backend.services.rca_service import analyze_root_cause
from backend.services.remediation_service import generate_remediation_plan
from backend.services.verification_service import verify_remediation


_incidents: dict[str, Incident] = {}


def _now():
    return datetime.now(timezone.utc)


def _audit(incident: Incident, event_type: str, description: str, severity: str = "INFO", user_id: str = "system"):
    incident.audit_event_ids.append(log_event(event_type, user_id, severity, f"{incident.incident_id}: {description}"))


def create_incident() -> Incident:
    groups = get_correlated_event_groups()
    if not groups:
        raise ValueError("No correlated incident conditions are currently active")
    group = groups[0]
    events = group["events"]
    severity = "CRITICAL" if any(e.severity == "CRITICAL" for e in events) else "HIGH"
    risk_score = max(e.risk_score for e in events)
    incident_id = f"INC-{uuid.uuid4().hex[:10].upper()}"
    incident = Incident(
        incident_id=incident_id, created_at=_now(), updated_at=_now(), title=group["title"],
        status="DETECTED", severity=severity, priority="HIGH", risk_score=risk_score,
        source_event_ids=[e.event_id for e in events], affected_components=group["components"],
        correlated_conditions=group["conditions"], approval_required=True,
    )
    _incidents[incident_id] = incident
    _audit(incident, "INCIDENT_DETECTED", "Incident detected from heterogeneous alerts.", severity)
    incident.status = "CORRELATING"
    _audit(incident, "EVENTS_CORRELATED", "Source events correlated into one incident.", severity)
    incident.updated_at = _now()
    return incident


def get_incident(incident_id: str) -> Incident | None:
    return _incidents.get(incident_id)


def list_incidents() -> list[Incident]:
    return sorted(_incidents.values(), key=lambda item: item.created_at, reverse=True)


def investigate_incident(incident: Incident) -> Incident:
    result = analyze_root_cause([{"description": condition} for condition in incident.correlated_conditions])
    incident.status = "INVESTIGATING"
    incident.investigation_summary = "Investigation found correlated machine stress signals; this is an explainable assessment, not a confirmed physical diagnosis."
    incident.probable_root_causes = result["probable_root_causes"]
    incident.root_cause_confidence = result["confidence"]
    incident.evidence = result["evidence"]
    incident.alternatives = result["alternatives"]
    _audit(incident, "INVESTIGATION_STARTED", "Investigation started.")
    _audit(incident, "RCA_COMPLETED", "Probable root cause assessment completed.")
    incident.updated_at = _now()
    return incident


def assess_incident(incident: Incident) -> Incident:
    impact = assess_impact(incident)
    incident.business_impact = {"category": impact["financial_impact_category"], "explanation": impact["explanation"]}
    incident.operational_impact = impact
    incident.status = "ASSESSED"
    _audit(incident, "IMPACT_ASSESSED", "Operational and qualitative business impact assessed.")
    incident.updated_at = _now()
    return incident


def prioritize_incident_state(incident: Incident) -> Incident:
    result = prioritize_incident(incident.severity, incident.risk_score, len(incident.source_event_ids), incident.affected_components, incident.operational_impact)
    incident.priority = result["priority"]
    incident.risk_score = result["priority_score"]
    return incident


def plan_remediation(incident: Incident) -> Incident:
    incident.remediation_steps = generate_remediation_plan(incident)
    incident.recommended_remediation = incident.remediation_steps[0].description
    incident.approval_required = any(step.approval_required for step in incident.remediation_steps)
    incident.approval_status = "PENDING" if incident.approval_required else "NOT_REQUIRED"
    incident.status = "AWAITING_APPROVAL" if incident.approval_required else "APPROVED"
    incident.action_status = "READY"
    _audit(incident, "REMEDIATION_PROPOSED", "Safe simulated remediation plan proposed.")
    _audit(incident, "APPROVAL_REQUESTED", "Human approval is required before execution.")
    incident.updated_at = _now()
    return incident


def approve_incident(incident: Incident, user_id: str) -> Incident:
    incident.approval_status = "APPROVED"
    incident.status = "APPROVED"
    _audit(incident, "REMEDIATION_APPROVED", "Remediation approved by authorized operator.", user_id=user_id)
    incident.updated_at = _now()
    return incident


def reject_incident(incident: Incident, user_id: str) -> Incident:
    incident.approval_status = "REJECTED"
    incident.status = "REJECTED"
    incident.action_status = "FAILED"
    _audit(incident, "REMEDIATION_REJECTED", "Remediation rejected by authorized operator.", user_id=user_id)
    incident.updated_at = _now()
    return incident


def execute_incident(incident: Incident, user_id: str) -> Incident:
    if incident.approval_required and incident.approval_status != "APPROVED":
        raise PermissionError("Incident remediation has not been approved")
    if not incident.remediation_steps or not all(step.safe_to_simulate for step in incident.remediation_steps):
        raise ValueError("Only safe simulated remediation can execute")
    incident.status = "REMEDIATING"
    incident.action_status = "COMPLETED"
    incident.verification["before_scenario"] = "AI01_MACHINE_INCIDENT"
    from backend.services.demo_controller import set_scenario
    set_scenario("RECOVERY")
    _audit(incident, "SIMULATED_ACTION_EXECUTED", "Safe simulated machine load reduction completed; no real equipment was controlled.", user_id=user_id)
    incident.updated_at = _now()
    return incident


def verify_incident(incident: Incident) -> Incident:
    result = verify_remediation(incident)
    incident.status = "VERIFYING"
    incident.verification_status = result["verification_status"]
    incident.verification_summary = result["explanation"]
    incident.verification = result
    _audit(incident, "VERIFICATION_COMPLETED", "Simulated remediation verification completed.")
    if result["improvement_detected"]:
        incident.status = "RESOLVED"
        _audit(incident, "INCIDENT_RESOLVED", "Incident resolved after successful simulated verification.")
    else:
        incident.status = "FAILED"
    incident.updated_at = _now()
    return incident


def run_resolution() -> Incident:
    incident = create_incident()
    investigate_incident(incident)
    assess_incident(incident)
    prioritize_incident_state(incident)
    plan_remediation(incident)
    return incident