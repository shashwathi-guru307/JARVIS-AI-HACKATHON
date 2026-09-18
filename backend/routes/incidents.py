from fastapi import APIRouter, Depends, HTTPException

from backend.services.auth_service import require_role
from backend.services.incident_service import (
    approve_incident, assess_incident, create_incident, execute_incident,
    get_incident, investigate_incident, list_incidents, plan_remediation,
    reject_incident, run_resolution, verify_incident,
)

router = APIRouter(prefix="/incidents", tags=["Incidents"])
operator = Depends(require_role(["admin", "operator"]))


def _get_or_404(incident_id: str):
    incident = get_incident(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.get("")
def incidents():
    return {"incidents": [incident.model_dump(mode="json") for incident in list_incidents()]}


@router.get("/{incident_id}")
def incident_detail(incident_id: str):
    return _get_or_404(incident_id).model_dump(mode="json")


@router.post("/detect")
def detect_incident():
    try:
        return create_incident().model_dump(mode="json")
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.post("/run-resolution")
def run_incident_resolution():
    try:
        return run_resolution().model_dump(mode="json")
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.post("/{incident_id}/investigate")
def investigate(incident_id: str):
    return investigate_incident(_get_or_404(incident_id)).model_dump(mode="json")


@router.post("/{incident_id}/assess")
def assess(incident_id: str):
    return assess_incident(_get_or_404(incident_id)).model_dump(mode="json")


@router.post("/{incident_id}/remediate")
def remediate(incident_id: str):
    return plan_remediation(_get_or_404(incident_id)).model_dump(mode="json")


@router.post("/{incident_id}/approve")
def approve(incident_id: str, user=operator):
    return approve_incident(_get_or_404(incident_id), user.get("sub", "authorized-operator")).model_dump(mode="json")


@router.post("/{incident_id}/reject")
def reject(incident_id: str, user=operator):
    return reject_incident(_get_or_404(incident_id), user.get("sub", "authorized-operator")).model_dump(mode="json")


@router.post("/{incident_id}/execute")
def execute(incident_id: str, user=operator):
    try:
        return execute_incident(_get_or_404(incident_id), user.get("sub", "authorized-operator")).model_dump(mode="json")
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.post("/{incident_id}/verify")
def verify(incident_id: str):
    return verify_incident(_get_or_404(incident_id)).model_dump(mode="json")