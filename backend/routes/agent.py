"""
POST /agent/analyze

Accepts two modes:
  mode=analyze (default) — full nine-dimension unified analysis
  mode=chat              — conversational voice/text agent with context
"""
import logging
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Literal
from backend.services.auth_service import require_role
from backend.services.incident_service import list_incidents, run_resolution

logger = logging.getLogger(__name__)
router = APIRouter()


class AnalyzeRequest(BaseModel):
    message: str = Field(..., min_length=1)
    mode: Literal["analyze", "chat"] = "analyze"
    system_context: str = ""                   # live snapshot injected by frontend
    conversation_history: list[dict] = []      # last N turns for follow-up support


@router.post("/agent/analyze", tags=["AI"])
async def analyze(
    body: AnalyzeRequest,
   
):
    """
    X.A.Z.E.L. unified analysis endpoint.
    mode=analyze  → nine-dimension structured JSON (Days 1–10)
    mode=chat     → plain-language conversational response for voice/text
    """
    from backend.crewai_runner import run_flow   # import locally to avoid circular deps

    message_lower = body.message.lower()
    active = next((item for item in list_incidents() if item.status not in ("RESOLVED", "REJECTED")), None)
    if "approve remediation" in message_lower or "approve the remediation" in message_lower:
        return {
            "status": "success",
            "risk_level": active.severity if active else "LOW",
            "summary": "Approval requires the authenticated incident approval control.",
            "reason": "X.A.Z.E.L. will not approve or execute remediation from an arbitrary language response.",
            "recommended_action": "Use the authenticated APPROVE REMEDIATION control on the incident panel.",
            "confidence": 1.0,
            "narrative_answer": "Remediation approval must use the authenticated incident approval flow. I did not approve or execute an action.",
        }
    if "investigate" in message_lower and "incident" in message_lower and active is None:
        try:
            active = run_resolution()
        except ValueError:
            active = None

    if active:
        body.system_context = (
            f"Active incident {active.incident_id}: {active.title}; status {active.status}; "
            f"severity {active.severity}; priority {active.priority}; "
            f"probable root cause {active.probable_root_causes}; "
            f"recommended remediation {active.recommended_remediation}.\n" + body.system_context
        )

    result = await run_flow(
        message=body.message,
        mode=body.mode,
        system_context=body.system_context,
        conversation_history=body.conversation_history,
    )
    return result