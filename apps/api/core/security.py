"""
ApnaSamaj – Security Utilities

JWT token creation / verification, OTP generation, and password hashing.

Design decisions:
  • python-jose for JWT (HS256 by default, configurable).
  • OTP is a random numeric string stored in Redis with TTL.
  • passlib[bcrypt] available if we ever need password-based auth.
  • All functions are pure / stateless – they receive config via params.
"""

from __future__ import annotations

import secrets
import string
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from apps.api.core.config import get_settings

settings = get_settings()

# ── Password Hashing (future use) ───────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ── JWT ──────────────────────────────────────────────────────────────────


def create_access_token(
    user_id: UUID,
    tenant_id: UUID | None = None,
    roles: list[str] | None = None,
    extra: dict[str, Any] | None = None,
) -> str:
    """Create a short-lived access token."""
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        "type": "access",
    }
    if tenant_id:
        payload["tenant_id"] = str(tenant_id)
    if roles:
        payload["roles"] = roles
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    user_id: UUID,
    session_id: UUID,
) -> str:
    """Create a long-lived refresh token tied to a session."""
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "session_id": str(session_id),
        "iat": now,
        "exp": now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT token. Raises JWTError on failure."""
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        raise


# ── OTP ──────────────────────────────────────────────────────────────────


def generate_otp(length: int | None = None) -> str:
    """Generate a cryptographically secure numeric OTP."""
    otp_length = length or settings.OTP_LENGTH
    return "".join(secrets.choice(string.digits) for _ in range(otp_length))
