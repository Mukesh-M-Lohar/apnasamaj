"""
ApnaSamaj – Auth Repository

Database operations for authentication:
  • User CRUD (find by mobile, by ID)
  • OTP record management
  • Session management (create, revoke, list)
  • UserTenantRole lookups
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.config import get_settings
from apps.api.modules.auth.models import (
    OTPRecord,
    Role,
    User,
    UserSession,
    UserTenantRole,
)

settings = get_settings()


class AuthRepository:
    """Handles all auth-related DB operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── User ─────────────────────────────────────────────────────────────

    async def find_user_by_mobile(self, mobile: str) -> User | None:
        stmt = select(User).where(User.mobile == mobile, User.is_deleted == False)  # noqa: E712
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_user_by_id(self, user_id: UUID) -> User | None:
        stmt = select(User).where(User.id == user_id, User.is_deleted == False)  # noqa: E712
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_user_by_google_id(self, google_id: str) -> User | None:
        stmt = select(User).where(User.google_id == google_id, User.is_deleted == False)  # noqa: E712
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_user_by_apple_id(self, apple_id: str) -> User | None:
        stmt = select(User).where(User.apple_id == apple_id, User.is_deleted == False)  # noqa: E712
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, mobile: str, full_name: str | None = None) -> User:
        user = User(
            mobile=mobile,
            full_name=full_name,
            is_verified=True,  # Verified via OTP
        )
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def update_last_login(self, user_id: UUID) -> None:
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(last_login_at=datetime.now(UTC))
        )
        await self._session.execute(stmt)

    # ── OTP ──────────────────────────────────────────────────────────────

    @staticmethod
    def hash_otp(otp: str) -> str:
        """Hash OTP for secure storage."""
        return hashlib.sha256(otp.encode()).hexdigest()

    async def create_otp_record(self, mobile: str, otp: str, purpose: str = "login") -> OTPRecord:
        # Invalidate any existing OTPs for this mobile
        await self._invalidate_existing_otps(mobile)

        record = OTPRecord(
            mobile=mobile,
            otp_hash=self.hash_otp(otp),
            purpose=purpose,
            max_attempts=settings.OTP_MAX_ATTEMPTS,
            expires_at=datetime.now(UTC) + timedelta(seconds=settings.OTP_EXPIRE_SECONDS),
        )
        self._session.add(record)
        await self._session.flush()
        return record

    async def find_valid_otp(self, mobile: str, purpose: str = "login") -> OTPRecord | None:
        now = datetime.now(UTC)
        stmt = (
            select(OTPRecord)
            .where(
                OTPRecord.mobile == mobile,
                OTPRecord.purpose == purpose,
                OTPRecord.is_verified == False,  # noqa: E712
                OTPRecord.expires_at > now,
            )
            .order_by(OTPRecord.created_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def increment_otp_attempts(self, otp_id: UUID) -> None:
        stmt = (
            update(OTPRecord)
            .where(OTPRecord.id == otp_id)
            .values(attempts=OTPRecord.attempts + 1)
        )
        await self._session.execute(stmt)

    async def mark_otp_verified(self, otp_id: UUID) -> None:
        stmt = (
            update(OTPRecord)
            .where(OTPRecord.id == otp_id)
            .values(is_verified=True)
        )
        await self._session.execute(stmt)

    async def _invalidate_existing_otps(self, mobile: str) -> None:
        stmt = (
            update(OTPRecord)
            .where(
                OTPRecord.mobile == mobile,
                OTPRecord.is_verified == False,  # noqa: E712
            )
            .values(is_verified=True)
        )
        await self._session.execute(stmt)

    # ── Sessions ─────────────────────────────────────────────────────────

    async def create_session(
        self,
        user_id: UUID,
        refresh_token_hash: str,
        expires_at: datetime,
        tenant_id: UUID | None = None,
        device_name: str | None = None,
        device_type: str | None = None,
        os: str | None = None,
        browser: str | None = None,
        ip_address: str | None = None,
    ) -> UserSession:
        session = UserSession(
            user_id=user_id,
            refresh_token_hash=refresh_token_hash,
            expires_at=expires_at,
            tenant_id=tenant_id,
            device_name=device_name,
            device_type=device_type,
            os=os,
            browser=browser,
            ip_address=ip_address,
        )
        self._session.add(session)
        await self._session.flush()
        await self._session.refresh(session)
        return session

    async def find_session_by_id(self, session_id: UUID) -> UserSession | None:
        stmt = select(UserSession).where(
            UserSession.id == session_id,
            UserSession.is_revoked == False,  # noqa: E712
            UserSession.is_deleted == False,  # noqa: E712
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_sessions_by_user(self, user_id: UUID) -> list[UserSession]:
        stmt = (
            select(UserSession)
            .where(
                UserSession.user_id == user_id,
                UserSession.is_revoked == False,  # noqa: E712
                UserSession.is_deleted == False,  # noqa: E712
            )
            .order_by(UserSession.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def revoke_session(self, session_id: UUID) -> bool:
        stmt = (
            update(UserSession)
            .where(UserSession.id == session_id)
            .values(is_revoked=True)
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def revoke_all_sessions(self, user_id: UUID, except_session_id: UUID | None = None) -> int:
        stmt = (
            update(UserSession)
            .where(
                UserSession.user_id == user_id,
                UserSession.is_revoked == False,  # noqa: E712
            )
            .values(is_revoked=True)
        )
        if except_session_id:
            stmt = stmt.where(UserSession.id != except_session_id)
        result = await self._session.execute(stmt)
        return result.rowcount

    async def delete_session(self, session_id: UUID) -> bool:
        stmt = delete(UserSession).where(UserSession.id == session_id)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    async def update_session_last_used(self, session_id: UUID, ip_address: str | None = None) -> None:
        values: dict = {"last_used_at": datetime.now(UTC)}
        if ip_address:
            values["ip_address"] = ip_address
        stmt = update(UserSession).where(UserSession.id == session_id).values(**values)
        await self._session.execute(stmt)

    # ── Roles ────────────────────────────────────────────────────────────

    async def get_user_roles_for_tenant(self, user_id: UUID, tenant_id: UUID) -> list[str]:
        stmt = (
            select(Role.name)
            .join(UserTenantRole, UserTenantRole.role_id == Role.id)
            .where(
                UserTenantRole.user_id == user_id,
                UserTenantRole.tenant_id == tenant_id,
                UserTenantRole.is_active == True,  # noqa: E712
            )
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_user_tenants(self, user_id: UUID) -> list[UUID]:
        """Get all tenant IDs a user belongs to."""
        stmt = (
            select(UserTenantRole.tenant_id)
            .where(
                UserTenantRole.user_id == user_id,
                UserTenantRole.is_active == True,  # noqa: E712
            )
            .distinct()
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_tenant_roles(self, tenant_id: UUID) -> list[Role]:
        from sqlalchemy import or_
        stmt = select(Role).where(
            or_(Role.tenant_id == tenant_id, Role.is_system == True)  # noqa: E712
        ).order_by(Role.name.asc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_role_by_id(self, role_id: UUID) -> Role | None:
        stmt = select(Role).where(Role.id == role_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def assign_role(self, user_id: UUID, tenant_id: UUID, role_id: UUID) -> UserTenantRole:
        stmt = select(UserTenantRole).where(
            UserTenantRole.user_id == user_id,
            UserTenantRole.tenant_id == tenant_id,
            UserTenantRole.role_id == role_id
        )
        result = await self._session.execute(stmt)
        utr = result.scalar_one_or_none()
        
        if utr:
            utr.is_active = True
        else:
            utr = UserTenantRole(
                user_id=user_id,
                tenant_id=tenant_id,
                role_id=role_id,
                is_active=True
            )
            self._session.add(utr)
            
        await self._session.flush()
        await self._session.refresh(utr)
        return utr

    async def revoke_role(self, user_id: UUID, tenant_id: UUID, role_id: UUID) -> bool:
        from sqlalchemy import delete
        stmt = delete(UserTenantRole).where(
            UserTenantRole.user_id == user_id,
            UserTenantRole.tenant_id == tenant_id,
            UserTenantRole.role_id == role_id
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0
