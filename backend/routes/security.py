import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.models.security_models import LoginRequest, TokenResponse
from backend.services.auth_service import authenticate_user, create_access_token, decode_token
from backend.services.audit_service import get_audit_log
from backend.services.security_service import (
    record_auth_failure, record_auth_success, record_rate_limit, record_api_spike,
    get_security_status, get_security_events,
)
from backend.services.transaction_risk_service import (
    generate_and_assess_transaction,
    get_recent_transactions,
    get_transaction_risks,
    get_transaction_summary,
)
from backend.utils.config import get_rate_limit_requests

logger = logging.getLogger(__name__)
router = APIRouter()
bearer = HTTPBearer(auto_error=False)

# ── Rate limiting (in-memory) ────────────────────────────────────────────────
_request_counts: dict[str, list] = defaultdict(list)
WINDOW_SECONDS = 60


def _check_rate_limit(client_ip: str, limit: int) -> bool:
    now = datetime.now(timezone.utc).timestamp()
    window = [t for t in _request_counts[client_ip] if now - t < WINDOW_SECONDS]
    _request_counts[client_ip] = window
    if len(window) >= limit:
        return False
    _request_counts[client_ip].append(now)
    return True


def rate_limit(request: Request, limit: int | None = None) -> None:
    cap = limit or get_rate_limit_requests()
    ip  = request.client.host if request.client else "unknown"
    if not _check_rate_limit(ip, cap):
        record_rate_limit(ip)
        raise HTTPException(status_code=429, detail="Too many requests. Please slow down.")


# ── Token dependency ─────────────────────────────────────────────────────────

def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict:
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required.")
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")
    return payload


def require_role(required: str):
    role_order = {"VIEWER": 0, "OPERATOR": 1, "ADMIN": 2}

    def checker(user: dict = Depends(get_current_user)) -> dict:
        user_role = user.get("role", "VIEWER")
        if role_order.get(user_role, -1) < role_order.get(required, 99):
            raise HTTPException(status_code=403, detail="Insufficient permissions.")
        return user

    return checker


# ── Background transaction loop ───────────────────────────────────────────────
_tx_task_started = False
TX_INTERVAL = 8   # seconds between synthetic transactions


async def _transaction_loop() -> None:
    while True:
        try:
            generate_and_assess_transaction()
        except Exception as exc:
            logger.error("Transaction loop error: %s", exc)
        await asyncio.sleep(TX_INTERVAL)


@router.on_event("startup")
async def start_transaction_loop() -> None:
    global _tx_task_started
    if not _tx_task_started:
        asyncio.create_task(_transaction_loop())
        _tx_task_started = True
        logger.info("💳  Transaction monitoring loop started (interval=%ds)", TX_INTERVAL)


# ── Auth endpoints ────────────────────────────────────────────────────────────

@router.post("/auth/login", response_model=TokenResponse, tags=["Security"])
def login(request: Request, body: LoginRequest):
    rate_limit(request, limit=10)
    user = authenticate_user(body.username, body.password)
    if not user:
        record_auth_failure(body.username)
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    record_auth_success(user["username"])
    token = create_access_token({"sub": user["username"], "role": user["role"]})
    return TokenResponse(
        access_token=token,
        role=user["role"],
        username=user["username"],
    )


@router.get("/auth/me", tags=["Security"])
def me(user: dict = Depends(get_current_user)):
    return {"username": user.get("sub"), "role": user.get("role")}


# ── Security status endpoints ─────────────────────────────────────────────────

@router.get("/security/status", tags=["Security"])
def security_status():
    return get_security_status().model_dump(mode="json")


@router.get("/security/history", tags=["Security"])
def security_history():
    events = get_security_events(50)
    return {"events": [e.model_dump(mode="json") for e in events]}


@router.get("/security/audit", tags=["Security"])
def audit_log(user: dict = Depends(require_role("OPERATOR"))):
    entries = get_audit_log(100)
    return {"audit": [e.model_dump(mode="json") for e in entries]}


# ── Transaction endpoints ─────────────────────────────────────────────────────

@router.get("/transactions/recent", tags=["Security"])
def transactions_recent(user: dict = Depends(get_current_user)):
    txs = get_recent_transactions(20)
    return {"transactions": [t.model_dump(mode="json") for t in txs]}


@router.get("/transactions/risk", tags=["Security"])
def transactions_risk(user: dict = Depends(get_current_user)):
    risks = get_transaction_risks(20)
    return {"risks": [r.model_dump(mode="json") for r in risks]}


@router.get("/transactions/summary", tags=["Security"])
def transactions_summary():
    return get_transaction_summary().model_dump(mode="json")