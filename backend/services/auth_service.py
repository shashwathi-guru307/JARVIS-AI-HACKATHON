import logging
import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.utils.config import (
    get_demo_mode,
    get_jwt_secret,
    get_jwt_expiration_minutes,
)


logger = logging.getLogger(__name__)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

security = HTTPBearer()


def _demo_password(name: str, development_default: str) -> str:
    """Read demo credentials from env; defaults are available only in demo mode."""
    value = os.getenv(name, "")
    if value:
        return value
    return development_default if get_demo_mode() else ""


def _build_demo_users() -> dict:
    users = {}
    for username, role, env_name, development_default in (
        ("admin", "ADMIN", "DEMO_ADMIN_PASSWORD", "admin123"),
        ("operator", "OPERATOR", "DEMO_OPERATOR_PASSWORD", "operator123"),
        ("viewer", "VIEWER", "DEMO_VIEWER_PASSWORD", "viewer123"),
    ):
        password = _demo_password(env_name, development_default)
        if password:
            users[username] = {"hashed": pwd_context.hash(password), "role": role}
    return users


DEMO_USERS = _build_demo_users()


# ============================================================
# PASSWORD VERIFICATION
# ============================================================

def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    return pwd_context.verify(plain, hashed)


# ============================================================
# USER AUTHENTICATION
# ============================================================

def authenticate_user(
    username: str,
    password: str,
) -> dict | None:
    """
    Authenticate a demo user.

    Returns:
        {
            "username": username,
            "role": role
        }

    Returns None if authentication fails.
    """

    user = DEMO_USERS.get(username)

    if not user:
        return None

    if not verify_password(password, user["hashed"]):
        return None

    return {
        "username": username,
        "role": user["role"],
    }


# ============================================================
# JWT TOKEN CREATION
# ============================================================

def create_access_token(data: dict) -> str:
    """Create a JWT access token."""

    payload = data.copy()

    expire = (
        datetime.now(timezone.utc)
        + timedelta(minutes=get_jwt_expiration_minutes())
    )

    payload["exp"] = expire

    return jwt.encode(
        payload,
        get_jwt_secret(),
        algorithm="HS256",
    )


# ============================================================
# JWT TOKEN DECODING
# ============================================================

def decode_token(token: str) -> dict | None:
    """
    Decode and validate a JWT token.

    Returns:
        Decoded payload if valid.
        None if invalid or expired.
    """

    try:
        return jwt.decode(
            token,
            get_jwt_secret(),
            algorithms=["HS256"],
        )

    except JWTError:
        return None


# ============================================================
# ROLE-BASED AUTHORIZATION
# ============================================================

def require_role(required_roles):
    """
    Require the authenticated user to have one of the specified roles.

    Supports:

        require_role("ADMIN")

    or:

        require_role(["ADMIN", "OPERATOR"])

    The comparison is case-insensitive, so these also work:

        require_role(["admin", "operator", "viewer"])
    """

    # Convert a single role into a list.
    if isinstance(required_roles, str):
        required_roles = [required_roles]

    # Normalize all required roles to uppercase.
    normalized_roles = {
        role.upper()
        for role in required_roles
    }

    def role_checker(
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ):
        # Extract Bearer token.
        token = credentials.credentials

        # Decode and validate JWT.
        payload = decode_token(token)

        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={
                    "WWW-Authenticate": "Bearer"
                },
            )

        # Get role from JWT.
        user_role = payload.get("role")

        if not user_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User role not found",
            )

        # Case-insensitive role comparison.
        if user_role.upper() not in normalized_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        # Return decoded user information.
        return payload

    return role_checker