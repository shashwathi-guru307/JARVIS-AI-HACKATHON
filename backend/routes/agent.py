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
    J.A.R.V.I.S. unified analysis endpoint.
    mode=analyze  → nine-dimension structured JSON (Days 1–10)
    mode=chat     → plain-language conversational response for voice/text
    """
    from backend.crewai_runner import run_flow   # import locally to avoid circular deps

    result = await run_flow(
        message=body.message,
        mode=body.mode,
        system_context=body.system_context,
        conversation_history=body.conversation_history,
    )
    return result