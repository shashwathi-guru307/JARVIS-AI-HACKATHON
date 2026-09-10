"""
GET /agent/context

Returns a compact system snapshot string suitable for injecting into the
chat agent as `system_context`. The frontend fetches this once before
sending a voice/text command so the agent is grounded in live data.
"""
import json
from fastapi import APIRouter, Depends
from backend.services.auth_service import require_role
from backend.services.orchestrator import get_system_snapshot

router = APIRouter()


@router.get("/agent/context", tags=["AI"])
def get_agent_context(
    _user=Depends(require_role(["admin", "operator", "viewer"])),
):
    """Returns a compact structured context string for the conversational agent."""
    snap = get_system_snapshot()
    domain = snap.get("domain_risks", {})
    corr   = snap.get("correlated_conditions", [])
    context = (
        f"System status: {snap.get('system_status', 'UNKNOWN')}. "
        f"System risk: {snap.get('system_risk', 'UNKNOWN')}. "
        f"System score: {snap.get('system_score', 'N/A')}. "
        f"Active alerts: {snap.get('active_alerts', 0)}. "
        f"Machine risk: {domain.get('machine', 'N/A')}. "
        f"Energy risk: {domain.get('energy', 'N/A')}. "
        f"Safety risk: {domain.get('safety', 'N/A')}. "
        f"Security risk: {domain.get('security', 'N/A')}. "
        f"Transaction risk: {domain.get('transaction', 'N/A')}. "
        f"Priority: {snap.get('priority', 'N/A')}. "
        + (f"Correlated conditions: {'; '.join(corr)}. " if corr else "")
        + f"Recommendation: {snap.get('recommendation', 'Continue monitoring.')}."
    )
    return {"context": context, "snapshot": snap}