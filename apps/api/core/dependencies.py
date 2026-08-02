"""
ApnaSamaj – FastAPI Dependencies

Centralized dependency injection functions for:
  • Database session
  • Current authenticated user
  • Current tenant context
  • Redis client
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.config import get_settings
from apps.api.core.database import get_db
from apps.api.core.exceptions import TenantException, UnauthorizedException
from apps.api.core.security import decode_token

settings = get_settings()
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any]:
    """
    Extract and validate the JWT from the Authorization header.

    Returns the decoded payload as a dict with at least:
      { "sub": "<user_id>", "tenant_id": "<tenant_id>", "roles": [...] }
    """
    if not credentials:
        raise UnauthorizedException("Missing authorization header")

    try:
        payload = decode_token(credentials.credentials)
    except JWTError:
        raise UnauthorizedException("Invalid or expired token")

    if payload.get("type") != "access":
        raise UnauthorizedException("Invalid token type")

    return payload


async def get_current_user_id(
    user: dict[str, Any] = Depends(get_current_user),
) -> UUID:
    """Extract the user UUID from the token payload."""
    return UUID(user["sub"])


async def get_current_tenant_id(
    user: dict[str, Any] = Depends(get_current_user),
) -> UUID:
    """Extract the tenant UUID from the token payload."""
    tenant_id = user.get("tenant_id")
    if not tenant_id:
        raise TenantException("No tenant context in token")
    return UUID(tenant_id)


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any] | None:
    """Like get_current_user but returns None for anonymous requests."""
    if not credentials:
        return None
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None
