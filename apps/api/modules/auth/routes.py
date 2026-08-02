"""
ApnaSamaj – Auth API Routes

All authentication endpoints:
  • POST /auth/otp/request     – Request OTP
  • POST /auth/otp/verify      – Verify OTP and get tokens
  • POST /auth/token/refresh   – Refresh access token
  • POST /auth/logout          – Logout (revoke session)
  • GET  /auth/me              – Current user profile
  • GET  /auth/sessions        – List active sessions
  • DELETE /auth/sessions/{id} – Revoke a session
  • POST /auth/google          – Google login (scaffold)
  • POST /auth/apple           – Apple login (scaffold)
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.base_schema import ApiResponse
from apps.api.core.database import get_db
from apps.api.core.dependencies import get_current_user, get_current_user_id
from apps.api.core.exceptions import AppException
from apps.api.modules.auth.schemas import (
    AppleLoginSchema,
    GoogleLoginSchema,
    OTPRequestSchema,
    OTPResponse,
    OTPVerifySchema,
    RefreshTokenRequest,
    SessionResponse,
    TokenResponse,
    UserProfileResponse,
)
from apps.api.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _get_client_ip(request: Request) -> str | None:
    """Extract client IP from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


# ── OTP Endpoints ────────────────────────────────────────────────────────


@router.post(
    "/otp/request",
    response_model=ApiResponse[OTPResponse],
    summary="Request OTP",
    description="Send a one-time password to the given mobile number.",
)
async def request_otp(
    body: OTPRequestSchema,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[OTPResponse]:
    service = AuthService(db)
    result = await service.request_otp(body.mobile)
    return ApiResponse(data=result)


@router.post(
    "/otp/verify",
    response_model=ApiResponse[TokenResponse],
    summary="Verify OTP",
    description="Verify OTP and receive JWT access + refresh tokens.",
)
async def verify_otp(
    body: OTPVerifySchema,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TokenResponse]:
    service = AuthService(db)
    result = await service.verify_otp(
        mobile=body.mobile,
        otp=body.otp,
        tenant_id=body.tenant_id,
        device_name=body.device_name,
        device_type=body.device_type,
        os=body.os,
        browser=body.browser,
        ip_address=_get_client_ip(request),
    )
    return ApiResponse(data=result)


# ── Token Endpoints ──────────────────────────────────────────────────────


@router.post(
    "/token/refresh",
    response_model=ApiResponse[TokenResponse],
    summary="Refresh Access Token",
    description="Exchange a valid refresh token for a new access token (with token rotation).",
)
async def refresh_token(
    body: RefreshTokenRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TokenResponse]:
    service = AuthService(db)
    result = await service.refresh_access_token(
        refresh_token=body.refresh_token,
        ip_address=_get_client_ip(request),
    )
    return ApiResponse(data=result)


# ── Logout ───────────────────────────────────────────────────────────────


@router.post(
    "/logout",
    response_model=ApiResponse[dict],
    summary="Logout",
    description="Revoke the current session's refresh token.",
)
async def logout(
    user_payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    service = AuthService(db)
    session_id = user_payload.get("session_id")
    if session_id:
        await service.logout(UUID(session_id))
    return ApiResponse(data={"message": "Logged out successfully"})


# ── Profile ──────────────────────────────────────────────────────────────


@router.get(
    "/me",
    response_model=ApiResponse[UserProfileResponse],
    summary="Get Current User Profile",
    description="Returns the authenticated user's profile and tenant memberships.",
)
async def get_me(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[UserProfileResponse]:
    service = AuthService(db)
    result = await service.get_profile(user_id)
    return ApiResponse(data=result)


# ── Session Management ──────────────────────────────────────────────────


@router.get(
    "/sessions",
    response_model=ApiResponse[list[SessionResponse]],
    summary="List Active Sessions",
    description="List all active login sessions / devices for the current user.",
)
async def list_sessions(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[list[SessionResponse]]:
    service = AuthService(db)
    result = await service.list_sessions(user_id)
    return ApiResponse(data=result)


@router.delete(
    "/sessions/{session_id}",
    response_model=ApiResponse[dict],
    summary="Revoke a Session",
    description="Revoke a specific login session / device.",
)
async def revoke_session(
    session_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    service = AuthService(db)
    revoked = await service.revoke_session(user_id, session_id)
    if not revoked:
        raise AppException("Session not found or already revoked", status_code=404)
    return ApiResponse(data={"message": "Session revoked successfully"})


# ── Social Login (scaffold) ─────────────────────────────────────────────


@router.post(
    "/google",
    response_model=ApiResponse[dict],
    summary="Google Login (Coming Soon)",
    description="Authenticate with Google ID token. Not yet implemented.",
)
async def google_login(body: GoogleLoginSchema) -> ApiResponse[dict]:
    raise AppException("Google login is not yet implemented", status_code=501, error_code="NOT_IMPLEMENTED")


@router.post(
    "/apple",
    response_model=ApiResponse[dict],
    summary="Apple Login (Coming Soon)",
    description="Authenticate with Apple identity token. Not yet implemented.",
)
async def apple_login(body: AppleLoginSchema) -> ApiResponse[dict]:
    raise AppException("Apple login is not yet implemented", status_code=501, error_code="NOT_IMPLEMENTED")
