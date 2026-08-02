"""
ApnaSamaj – Community (Tenant) Service

Business logic for community management:
  • Create community (with slug uniqueness)
  • Onboard community (create + assign admin role)
  • Update community details and settings
  • List, search, paginate communities
  • Get community stats (dashboard)
  • Activate / deactivate / delete
  • Invite members to community

Design decisions:
  • Onboarding creates a community AND assigns the current user as
    Community Admin in one atomic operation.
  • Slug uniqueness is checked at the service layer for a friendly error,
    with a DB unique constraint as a safety net.
  • Stats are computed from cross-module counts (members, donations, etc.)
    using lazy imports to avoid circular dependencies.
"""

from __future__ import annotations

import logging
import math
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from apps.api.core.config import get_settings
from apps.api.core.exceptions import (
    AlreadyExistsException,
    ForbiddenException,
    NotFoundException,
)
from apps.api.modules.tenant.repository import CommunityRepository
from apps.api.modules.tenant.schemas import (
    CommunityCreateSchema,
    CommunityListResponse,
    CommunityOnboardResponse,
    CommunityOnboardSchema,
    CommunityResponse,
    CommunitySettingsSchema,
    CommunityStatsResponse,
    CommunityUpdateSchema,
)

logger = logging.getLogger(__name__)
settings = get_settings()


class CommunityService:
    """Community management business logic."""

    def __init__(self, session: AsyncSession) -> None:
        self._repo = CommunityRepository(session)
        self._session = session

    # ── Create ───────────────────────────────────────────────────────────

    async def create_community(
        self,
        data: CommunityCreateSchema,
        created_by: UUID | None = None,
    ) -> CommunityResponse:
        """Create a new community (tenant)."""

        # Check slug uniqueness
        if await self._repo.slug_exists(data.slug):
            raise AlreadyExistsException("Community", field=f"slug '{data.slug}'")

        tenant = await self._repo.create(
            data=data.model_dump(exclude_none=True),
            created_by=created_by,
        )

        logger.info("Community created: %s (slug=%s)", tenant.name, tenant.slug)
        return CommunityResponse.model_validate(tenant)

    # ── Onboard ──────────────────────────────────────────────────────────

    async def onboard_community(
        self,
        data: CommunityOnboardSchema,
        user_id: UUID,
    ) -> CommunityOnboardResponse:
        """
        Create a community and assign the requesting user as Community Admin.

        This is the primary entry point for new community registration.
        """
        from apps.api.modules.auth.models import Role, UserTenantRole

        # Check slug uniqueness
        if await self._repo.slug_exists(data.community.slug):
            raise AlreadyExistsException("Community", field=f"slug '{data.community.slug}'")

        # Create community
        tenant = await self._repo.create(
            data=data.community.model_dump(exclude_none=True),
            created_by=user_id,
        )

        # Find or create 'community_admin' role
        admin_role = await self._session.execute(
            select(Role).where(
                Role.name == "community_admin",
                Role.is_system == True,  # noqa: E712
            )
        )
        role = admin_role.scalar_one_or_none()

        if role:
            # Assign user as community admin
            user_tenant_role = UserTenantRole(
                user_id=user_id,
                tenant_id=tenant.id,
                role_id=role.id,
            )
            self._session.add(user_tenant_role)
            await self._session.flush()

        # Optionally update user's full_name if provided
        if data.admin_full_name:
            from apps.api.modules.auth.models import User
            from sqlalchemy import update

            await self._session.execute(
                update(User)
                .where(User.id == user_id)
                .values(full_name=data.admin_full_name)
            )

        logger.info(
            "Community onboarded: %s by user %s",
            tenant.name,
            user_id,
        )

        return CommunityOnboardResponse(
            community=CommunityResponse.model_validate(tenant),
            role="community_admin",
        )

    # ── Read ─────────────────────────────────────────────────────────────

    async def get_community(self, community_id: UUID) -> CommunityResponse:
        """Get a single community by ID."""
        tenant = await self._repo.get_by_id(community_id)
        if not tenant:
            raise NotFoundException("Community", str(community_id))
        return CommunityResponse.model_validate(tenant)

    async def get_community_by_slug(self, slug: str) -> CommunityResponse:
        """Get a community by its URL slug (public lookup)."""
        tenant = await self._repo.get_by_slug(slug)
        if not tenant:
            raise NotFoundException("Community", slug)
        return CommunityResponse.model_validate(tenant)

    async def list_communities(
        self,
        page: int = 1,
        per_page: int = 20,
        search: str | None = None,
        is_active: bool | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> dict[str, Any]:
        """List communities with pagination, search, and filtering."""
        total = await self._repo.count(search=search, is_active=is_active)
        total_pages = math.ceil(total / per_page) if per_page > 0 else 0
        offset = (page - 1) * per_page

        tenants = await self._repo.get_all(
            offset=offset,
            limit=per_page,
            search=search,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        items = [
            CommunityListResponse(
                id=t.id,
                name=t.name,
                slug=t.slug,
                logo_url=t.logo_url,
                city=t.city,
                state=t.state,
                is_active=t.is_active,
                member_count=0,  # TODO: compute from member count
                created_at=t.created_at,
            )
            for t in tenants
        ]

        return {
            "items": items,
            "meta": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            },
        }

    async def get_my_communities(self, user_id: UUID) -> list[CommunityListResponse]:
        """Get all communities the current user belongs to."""
        tenants = await self._repo.get_user_communities(user_id)
        return [
            CommunityListResponse(
                id=t.id,
                name=t.name,
                slug=t.slug,
                logo_url=t.logo_url,
                city=t.city,
                state=t.state,
                is_active=t.is_active,
                member_count=0,
                created_at=t.created_at,
            )
            for t in tenants
        ]

    # ── Update ───────────────────────────────────────────────────────────

    async def update_community(
        self,
        community_id: UUID,
        data: CommunityUpdateSchema,
        updated_by: UUID | None = None,
    ) -> CommunityResponse:
        """Partially update community details."""
        tenant = await self._repo.update(
            tenant_id=community_id,
            data=data.model_dump(exclude_unset=True),
            updated_by=updated_by,
        )
        if not tenant:
            raise NotFoundException("Community", str(community_id))

        logger.info("Community updated: %s", tenant.name)
        return CommunityResponse.model_validate(tenant)

    async def update_settings(
        self,
        community_id: UUID,
        data: CommunitySettingsSchema,
        updated_by: UUID | None = None,
    ) -> CommunityResponse:
        """Update community settings (merged with existing)."""
        tenant = await self._repo.update_settings(
            tenant_id=community_id,
            settings=data.settings,
            updated_by=updated_by,
        )
        if not tenant:
            raise NotFoundException("Community", str(community_id))
        return CommunityResponse.model_validate(tenant)

    # ── Activate / Deactivate ────────────────────────────────────────────

    async def activate_community(
        self, community_id: UUID, updated_by: UUID | None = None
    ) -> dict:
        success = await self._repo.set_active(community_id, True, updated_by)
        if not success:
            raise NotFoundException("Community", str(community_id))
        return {"message": "Community activated"}

    async def deactivate_community(
        self, community_id: UUID, updated_by: UUID | None = None
    ) -> dict:
        success = await self._repo.set_active(community_id, False, updated_by)
        if not success:
            raise NotFoundException("Community", str(community_id))
        return {"message": "Community deactivated"}

    # ── Delete ───────────────────────────────────────────────────────────

    async def delete_community(
        self, community_id: UUID, deleted_by: UUID | None = None
    ) -> dict:
        """Soft-delete a community (Super Admin only)."""
        success = await self._repo.soft_delete(community_id, deleted_by)
        if not success:
            raise NotFoundException("Community", str(community_id))
        logger.warning("Community soft-deleted: %s by %s", community_id, deleted_by)
        return {"message": "Community deleted"}

    # ── Stats ────────────────────────────────────────────────────────────

    async def get_community_stats(self, community_id: UUID) -> CommunityStatsResponse:
        """Get dashboard-level stats for a community."""
        # Verify community exists
        tenant = await self._repo.get_by_id(community_id)
        if not tenant:
            raise NotFoundException("Community", str(community_id))

        # Import models lazily to avoid circular deps
        from apps.api.modules.member.models import Member
        from apps.api.modules.family.models import Family
        from apps.api.modules.donation.models import Donation
        from apps.api.modules.event.models import Event
        from apps.api.modules.volunteer.models import Volunteer
        from apps.api.modules.complaint.models import Complaint

        async def _count(model: type, extra_filter=None) -> int:
            stmt = (
                select(func.count())
                .select_from(model)
                .where(
                    model.tenant_id == community_id,
                    model.is_deleted == False,  # noqa: E712
                )
            )
            if extra_filter is not None:
                stmt = stmt.where(extra_filter)
            result = await self._session.execute(stmt)
            return result.scalar_one()

        total_members = await _count(Member)
        active_members = await _count(Member, Member.status == "active")
        total_families = await _count(Family)
        total_donations = await _count(Donation)
        total_events = await _count(Event)
        total_volunteers = await _count(Volunteer)
        open_complaints = await _count(Complaint, Complaint.status.in_(["open", "in_progress"]))

        return CommunityStatsResponse(
            total_members=total_members,
            active_members=active_members,
            total_families=total_families,
            total_donations=total_donations,
            total_events=total_events,
            total_volunteers=total_volunteers,
            open_complaints=open_complaints,
        )

    # ── Invite ───────────────────────────────────────────────────────────

    async def invite_member(
        self,
        community_id: UUID,
        mobile: str,
        role_name: str = "member",
        full_name: str | None = None,
        invited_by: UUID | None = None,
    ) -> dict:
        """
        Invite a user to join a community.

        If the user doesn't exist yet, they'll be auto-created on their
        first OTP login and will already have the community role assigned.
        """
        from apps.api.modules.auth.models import Role, User, UserTenantRole

        # Verify community exists
        tenant = await self._repo.get_by_id(community_id)
        if not tenant:
            raise NotFoundException("Community", str(community_id))

        # Find or create user
        user_result = await self._session.execute(
            select(User).where(User.mobile == mobile, User.is_deleted == False)  # noqa: E712
        )
        user = user_result.scalar_one_or_none()

        if not user:
            user = User(mobile=mobile, full_name=full_name)
            self._session.add(user)
            await self._session.flush()
            await self._session.refresh(user)

        # Check if already a member of this community
        existing = await self._session.execute(
            select(UserTenantRole).where(
                UserTenantRole.user_id == user.id,
                UserTenantRole.tenant_id == community_id,
                UserTenantRole.is_active == True,  # noqa: E712
            )
        )
        if existing.scalar_one_or_none():
            raise AlreadyExistsException("Member", field="this community")

        # Find the role
        role_result = await self._session.execute(
            select(Role).where(Role.name == role_name)
        )
        role = role_result.scalar_one_or_none()
        if not role:
            raise NotFoundException("Role", role_name)

        # Assign role
        user_tenant_role = UserTenantRole(
            user_id=user.id,
            tenant_id=community_id,
            role_id=role.id,
        )
        self._session.add(user_tenant_role)
        await self._session.flush()

        logger.info(
            "User %s invited to community %s with role %s",
            mobile, tenant.name, role_name,
        )

        return {
            "message": f"User {mobile} invited as {role_name}",
            "user_id": str(user.id),
        }
