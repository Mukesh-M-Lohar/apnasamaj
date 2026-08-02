"""
ApnaSamaj – Auth Service

Business logic for authentication:
  • Request OTP → generate, store, (send via SMS – stubbed)
  • Verify OTP → validate, create/find user, create session, issue tokens
  • Refresh token → validate refresh token, issue new access token
  • Logout → revoke session
  • Get profile → return user with tenants
  • Session management → list/revoke sessions

Design decisions:
  • Service layer orchestrates repository calls and security utilities.
  • OTP sending is stubbed (logs to console) – plug in SMS provider later.
  • New users are auto-created on first OTP verification (frictionless onboarding).
  • Refresh tokens are hashed before storage (never stored in plaintext).
"""

from __future__ import annotations

import hashlib
import logging
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.config import get_settings
from apps.api.core.exceptions import (
    OTPException,
    RateLimitException,
    UnauthorizedException,
)
from apps.api.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_otp,
)
from apps.api.modules.auth.repository import AuthRepository
from apps.api.modules.auth.schemas import (
    OTPResponse,
    SessionResponse,
    TokenResponse,
    UserProfileResponse,
    UserResponse,
)

logger = logging.getLogger(__name__)
settings = get_settings()


class AuthService:
    """Authentication business logic."""

    def __init__(self, session: AsyncSession) -> None:
        self._repo = AuthRepository(session)

    # ── OTP Request ──────────────────────────────────────────────────────

    async def request_otp(self, mobile: str) -> OTPResponse:
        """Generate and 'send' an OTP to the given mobile number."""

        # Check for rate limiting (cooldown between OTP requests)
        existing = await self._repo.find_valid_otp(mobile)
        if existing:
            elapsed = (datetime.now(UTC) - existing.created_at).total_seconds()
            if elapsed < settings.OTP_RESEND_COOLDOWN_SECONDS:
                remaining = int(settings.OTP_RESEND_COOLDOWN_SECONDS - elapsed)
                raise RateLimitException(
                    message=f"Please wait {remaining} seconds before requesting a new OTP"
                )

        otp = generate_otp()
        await self._repo.create_otp_record(mobile, otp)

        # TODO: Send OTP via SMS provider (Twilio, MSG91, etc.)
        # For now, log it (NEVER do this in production)
        logger.info("OTP for %s: %s (DEV ONLY – remove in production)", mobile, otp)

        return OTPResponse(
            message="OTP sent successfully",
            expires_in=settings.OTP_EXPIRE_SECONDS,
            mobile=mobile,
        )

    # ── OTP Verify ───────────────────────────────────────────────────────

    async def verify_otp(
        self,
        mobile: str,
        otp: str,
        tenant_id: UUID | None = None,
        device_name: str | None = None,
        device_type: str | None = None,
        os: str | None = None,
        browser: str | None = None,
        ip_address: str | None = None,
    ) -> TokenResponse:
        """Verify OTP, create/find user, issue tokens."""

        otp_record = await self._repo.find_valid_otp(mobile)
        if not otp_record:
            raise OTPException("No valid OTP found. Please request a new one.")

        # Check attempts
        if otp_record.attempts >= otp_record.max_attempts:
            raise OTPException("Maximum OTP attempts exceeded. Please request a new OTP.")

        # Verify hash
        otp_hash = AuthRepository.hash_otp(otp)
        if otp_hash != otp_record.otp_hash:
            await self._repo.increment_otp_attempts(otp_record.id)
            remaining = otp_record.max_attempts - otp_record.attempts - 1
            raise OTPException(f"Invalid OTP. {remaining} attempts remaining.")

        # Mark OTP as verified
        await self._repo.mark_otp_verified(otp_record.id)

        # Find or create user
        user = await self._repo.find_user_by_mobile(mobile)
        if not user:
            user = await self._repo.create_user(mobile)

        # Update last login
        await self._repo.update_last_login(user.id)

        # Get roles for tenant (if specified)
        roles: list[str] = []
        if user.is_super_admin:
            roles = ["super_admin"]
        elif tenant_id:
            roles = await self._repo.get_user_roles_for_tenant(user.id, tenant_id)

        # Create session
        session_record = await self._repo.create_session(
            user_id=user.id,
            refresh_token_hash="placeholder",  # Will update after generating token
            expires_at=datetime.now(UTC) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
            tenant_id=tenant_id,
            device_name=device_name,
            device_type=device_type,
            os=os,
            browser=browser,
            ip_address=ip_address,
        )

        # Generate tokens
        access_token = create_access_token(
            user_id=user.id,
            tenant_id=tenant_id,
            roles=roles,
        )
        refresh_token = create_refresh_token(
            user_id=user.id,
            session_id=session_record.id,
        )

        # Store hashed refresh token
        session_record.refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse(
                id=user.id,
                mobile=user.mobile,
                email=user.email,
                full_name=user.full_name,
                avatar_url=user.avatar_url,
                is_verified=user.is_verified,
                is_super_admin=user.is_super_admin,
                roles=roles,
                created_at=user.created_at,
            ),
        )

    # ── Token Refresh ────────────────────────────────────────────────────

    async def refresh_access_token(
        self,
        refresh_token: str,
        ip_address: str | None = None,
    ) -> TokenResponse:
        """Validate refresh token and issue a new access token."""
        try:
            payload = decode_token(refresh_token)
        except Exception:
            raise UnauthorizedException("Invalid refresh token")

        if payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid token type")

        session_id = UUID(payload["session_id"])
        user_id = UUID(payload["sub"])

        # Find the session
        session_record = await self._repo.find_session_by_id(session_id)
        if not session_record:
            raise UnauthorizedException("Session not found or revoked")

        # Verify the refresh token hash matches
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        if token_hash != session_record.refresh_token_hash:
            raise UnauthorizedException("Invalid refresh token")

        # Check expiry
        if session_record.expires_at < datetime.now(UTC):
            raise UnauthorizedException("Session expired")

        # Find user
        user = await self._repo.find_user_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")

        # Update session last used
        await self._repo.update_session_last_used(session_id, ip_address)

        # Get roles
        roles: list[str] = []
        tenant_id = session_record.tenant_id
        if user.is_super_admin:
            roles = ["super_admin"]
        elif tenant_id:
            roles = await self._repo.get_user_roles_for_tenant(user.id, tenant_id)

        # Issue new access token
        access_token = create_access_token(
            user_id=user.id,
            tenant_id=tenant_id,
            roles=roles,
        )

        # Issue new refresh token (rotation)
        new_refresh_token = create_refresh_token(
            user_id=user.id,
            session_id=session_id,
        )
        session_record.refresh_token_hash = hashlib.sha256(new_refresh_token.encode()).hexdigest()

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse(
                id=user.id,
                mobile=user.mobile,
                email=user.email,
                full_name=user.full_name,
                avatar_url=user.avatar_url,
                is_verified=user.is_verified,
                is_super_admin=user.is_super_admin,
                roles=roles,
                created_at=user.created_at,
            ),
        )

    # ── Logout ───────────────────────────────────────────────────────────

    async def logout(self, session_id: UUID) -> bool:
        """Revoke the current session."""
        return await self._repo.revoke_session(session_id)

    # ── Profile ──────────────────────────────────────────────────────────

    async def get_profile(self, user_id: UUID) -> UserProfileResponse:
        """Get the full user profile with tenant memberships."""
        user = await self._repo.find_user_by_id(user_id)
        if not user:
            raise UnauthorizedException("User not found")

        tenant_ids = await self._repo.get_user_tenants(user_id)

        return UserProfileResponse(
            id=user.id,
            mobile=user.mobile,
            email=user.email,
            full_name=user.full_name,
            avatar_url=user.avatar_url,
            is_verified=user.is_verified,
            is_super_admin=user.is_super_admin,
            tenants=[],  # TODO: populate with tenant details
            created_at=user.created_at,
        )

    # ── Session Management ───────────────────────────────────────────────

    async def list_sessions(self, user_id: UUID) -> list[SessionResponse]:
        """List all active sessions for a user."""
        sessions = await self._repo.find_sessions_by_user(user_id)
        return [
            SessionResponse(
                id=s.id,
                device_name=s.device_name,
                device_type=s.device_type,
                os=s.os,
                browser=s.browser,
                ip_address=s.ip_address,
                is_revoked=s.is_revoked,
                last_used_at=s.last_used_at,
                created_at=s.created_at,
            )
            for s in sessions
        ]

    async def revoke_session(self, user_id: UUID, session_id: UUID) -> bool:
        """Revoke a specific session (must belong to the user)."""
        session = await self._repo.find_session_by_id(session_id)
        if not session or session.user_id != user_id:
            return False
        return await self._repo.revoke_session(session_id)

    # ── Roles ────────────────────────────────────────────────────────────
    
    async def get_tenant_roles(self, tenant_id: UUID) -> list[dict]:
        roles = await self._repo.get_tenant_roles(tenant_id)
        return [
            {
                "id": r.id,
                "name": r.name,
                "display_name": r.display_name,
                "description": r.description,
                "is_system": r.is_system
            } for r in roles
        ]

    async def assign_role(self, user_id: UUID, tenant_id: UUID, role_id: UUID) -> dict:
        user = await self._repo.find_user_by_id(user_id)
        if not user:
            raise NotFoundException("User", str(user_id))
            
        role = await self._repo.get_role_by_id(role_id)
        if not role:
            raise NotFoundException("Role", str(role_id))
            
        utr = await self._repo.assign_role(user_id, tenant_id, role_id)
        return {
            "id": utr.id,
            "user_id": utr.user_id,
            "tenant_id": utr.tenant_id,
            "role_id": utr.role_id,
            "is_active": utr.is_active,
            "created_at": utr.created_at
        }
        
    async def revoke_role(self, user_id: UUID, tenant_id: UUID, role_id: UUID) -> bool:
        return await self._repo.revoke_role(user_id, tenant_id, role_id)
