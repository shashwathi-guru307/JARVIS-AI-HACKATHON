"""
Demo control endpoints — only active when DEMO_MODE=true.
"""
import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.utils.config import DEMO_MODE, VALID_SCENARIOS
from backend.services.demo_controller import get_scenario, set_scenario
from backend.services.auth_service import require_role  # reuse existing auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/demo", tags=["Demo"])


class ScenarioRequest(BaseModel):
    scenario: str


@router.get("/status")
def demo_status():
    if not DEMO_MODE:
        return {"demo_mode": False, "message": "Demo mode is disabled."}
    return {
        "demo_mode": True,
        "current_scenario": get_scenario(),
        "available_scenarios": sorted(VALID_SCENARIOS),
    }


@router.post("/scenario")
def set_demo_scenario(
    body: ScenarioRequest,
    _user=Depends(require_role(["admin", "operator"])),
):
    if not DEMO_MODE:
        raise HTTPException(status_code=403, detail="Demo mode is disabled.")
    try:
        new = set_scenario(body.scenario)
        return {"success": True, "scenario": new}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))