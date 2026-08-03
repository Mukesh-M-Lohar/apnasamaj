"""
ApnaSamaj – Community (Tenant) Repository

Database operations for community management.

Design decisions:
  • Tenant is a GlobalBaseModel (no tenant_id on itself).
  • Slug uniqueness enforced at the DB level + checked before insert.
  • Stats queries use efficient COUNT aggregations via sub-selects.
  • find_by_slug for public community lookup.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Select, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.modules.tenant.models import Tenant


class CommunityRepository:
    """Handles all community/tenant DB operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Helpers ──────────────────────────────────────────────────────────

    def _active_query(self) -> Select:
        return select(Tenant).where(Tenant.is_deleted == False)  # noqa: E712

    # ── Create ───────────────────────────────────────────────────────────

    async def create(self, data: dict[str, Any], created_by: UUID | None = None) -> Tenant:
        tenant = Tenant(created_by=created_by, updated_by=created_by, **data)
        self._session.add(tenant)
        await self._session.flush()
        await self._session.refresh(tenant)
        return tenant

    # ── Read ─────────────────────────────────────────────────────────────

    async def get_by_id(self, tenant_id: UUID) -> Tenant | None:
        stmt = self._active_query().where(Tenant.id == tenant_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Tenant | None:
        stmt = self._active_query().where(Tenant.slug == slug)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def slug_exists(self, slug: str, exclude_id: UUID | None = None) -> bool:
        stmt = (
            select(func.count())
            .select_from(Tenant)
            .where(Tenant.slug == slug, Tenant.is_deleted == False)  # noqa: E712
        )
        if exclude_id:
            stmt = stmt.where(Tenant.id != exclude_id)
        result = await self._session.execute(stmt)
        return result.scalar_one() > 0

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
        search: str | None = None,
        is_active: bool | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> list[Tenant]:
        stmt = self._active_query()

        if search:
            search_filter = f"%{search}%"
            stmt = stmt.where(
                Tenant.name.ilike(search_filter) | Tenant.slug.ilike(search_filter) | Tenant.city.ilike(search_filter)
            )

        if is_active is not None:
            stmt = stmt.where(Tenant.is_active == is_active)

        sort_column = getattr(Tenant, sort_by, Tenant.created_at)
        stmt = stmt.order_by(sort_column.desc() if sort_order == "desc" else sort_column.asc())
        stmt = stmt.offset(offset).limit(limit)

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count(self, search: str | None = None, is_active: bool | None = None) -> int:
        stmt = select(func.count()).select_from(Tenant).where(Tenant.is_deleted == False)  # noqa: E712
        if search:
            search_filter = f"%{search}%"
            stmt = stmt.where(
                Tenant.name.ilike(search_filter) | Tenant.slug.ilike(search_filter) | Tenant.city.ilike(search_filter)
            )
        if is_active is not None:
            stmt = stmt.where(Tenant.is_active == is_active)

        result = await self._session.execute(stmt)
        return result.scalar_one()

    # ── Update ───────────────────────────────────────────────────────────

    async def update(self, tenant_id: UUID, data: dict[str, Any], updated_by: UUID | None = None) -> Tenant | None:
        tenant = await self.get_by_id(tenant_id)
        if not tenant:
            return None

        for key, value in data.items():
            if value is not None and hasattr(tenant, key):
                setattr(tenant, key, value)

        if updated_by:
            tenant.updated_by = updated_by

        await self._session.flush()
        await self._session.refresh(tenant)
        return tenant

    async def update_settings(self, tenant_id: UUID, settings: dict, updated_by: UUID | None = None) -> Tenant | None:
        tenant = await self.get_by_id(tenant_id)
        if not tenant:
            return None

        # Merge with existing settings
        existing = tenant.settings or {}
        existing.update(settings)
        tenant.settings = existing

        if updated_by:
            tenant.updated_by = updated_by

        await self._session.flush()
        await self._session.refresh(tenant)
        return tenant

    # ── Deactivate / Reactivate ──────────────────────────────────────────

    async def set_active(self, tenant_id: UUID, is_active: bool, updated_by: UUID | None = None) -> bool:
        stmt = update(Tenant).where(Tenant.id == tenant_id).values(is_active=is_active, updated_by=updated_by)
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    # ── Soft Delete ──────────────────────────────────────────────────────

    async def soft_delete(self, tenant_id: UUID, deleted_by: UUID | None = None) -> bool:
        tenant = await self.get_by_id(tenant_id)
        if not tenant:
            return False
        tenant.is_deleted = True
        tenant.deleted_at = datetime.now(UTC)
        tenant.is_active = False
        if deleted_by:
            tenant.updated_by = deleted_by
        await self._session.flush()
        return True

    # ── Tenant Membership Queries ────────────────────────────────────────

    async def get_user_communities(self, user_id: UUID) -> list[Tenant]:
        """Get all communities a user belongs to (via user_tenant_roles)."""
        from apps.api.modules.auth.models import UserTenantRole

        stmt = (
            select(Tenant)
            .join(UserTenantRole, UserTenantRole.tenant_id == Tenant.id)
            .where(
                UserTenantRole.user_id == user_id,
                UserTenantRole.is_active == True,  # noqa: E712
                Tenant.is_deleted == False,  # noqa: E712
                Tenant.is_active == True,  # noqa: E712
            )
            .distinct()
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
