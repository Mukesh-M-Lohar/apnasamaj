"""
ApnaSamaj – Member Repository

Database operations for community members.
Includes advanced directory search with filtering and sorting.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import Select, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.modules.member.models import Member


class MemberRepository:
    """Handles member DB operations scoped to a tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self._session = session
        self.tenant_id = tenant_id

    def _base_query(self) -> Select:
        return select(Member).where(
            Member.tenant_id == self.tenant_id,
            Member.is_deleted == False,  # noqa: E712
        )

    # ── Create ───────────────────────────────────────────────────────────

    async def create(self, data: dict[str, Any], created_by: UUID | None = None) -> Member:
        member = Member(
            tenant_id=self.tenant_id,
            created_by=created_by,
            updated_by=created_by,
            **data,
        )
        self._session.add(member)
        await self._session.flush()
        await self._session.refresh(member)
        return member

    # ── Read ─────────────────────────────────────────────────────────────

    async def get_by_id(self, member_id: UUID) -> Member | None:
        stmt = self._base_query().where(Member.id == member_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: UUID) -> Member | None:
        stmt = self._base_query().where(Member.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_paginated(
        self,
        offset: int = 0,
        limit: int = 20,
        search: str | None = None,
        status: str | None = None,
        blood_group: str | None = None,
        city: str | None = None,
        gender: str | None = None,
        sort_by: str = "first_name",
        sort_order: str = "asc",
    ) -> tuple[list[Member], int]:
        """Get members with filters, search, sorting, and pagination."""
        stmt = self._base_query()
        count_stmt = (
            select(func.count())
            .select_from(Member)
            .where(
                Member.tenant_id == self.tenant_id,
                Member.is_deleted == False,  # noqa: E712
            )
        )

        # Filters
        if status:
            stmt = stmt.where(Member.status == status)
            count_stmt = count_stmt.where(Member.status == status)
        if blood_group:
            stmt = stmt.where(Member.blood_group == blood_group)
            count_stmt = count_stmt.where(Member.blood_group == blood_group)
        if city:
            stmt = stmt.where(Member.city.ilike(f"%{city}%"))
            count_stmt = count_stmt.where(Member.city.ilike(f"%{city}%"))
        if gender:
            stmt = stmt.where(Member.gender == gender)
            count_stmt = count_stmt.where(Member.gender == gender)

        # Search (fuzzy matching on name, mobile, email)
        if search:
            search_filter = f"%{search}%"
            condition = or_(
                Member.first_name.ilike(search_filter),
                Member.last_name.ilike(search_filter),
                Member.mobile.ilike(search_filter),
                Member.email.ilike(search_filter),
                Member.membership_number.ilike(search_filter),
            )
            stmt = stmt.where(condition)
            count_stmt = count_stmt.where(condition)

        # Count total matching records
        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        # Sorting
        sort_column = getattr(Member, sort_by, Member.first_name)
        stmt = stmt.order_by(sort_column.desc() if sort_order == "desc" else sort_column.asc())

        # Pagination
        stmt = stmt.offset(offset).limit(limit)

        result = await self._session.execute(stmt)
        members = list(result.scalars().all())

        return members, total

    # ── Update ───────────────────────────────────────────────────────────

    async def update(self, member_id: UUID, data: dict[str, Any], updated_by: UUID | None = None) -> Member | None:
        member = await self.get_by_id(member_id)
        if not member:
            return None

        for key, value in data.items():
            if value is not None and hasattr(member, key):
                setattr(member, key, value)

        if updated_by:
            member.updated_by = updated_by

        await self._session.flush()
        await self._session.refresh(member)
        return member

    async def link_user(self, member_id: UUID, user_id: UUID, updated_by: UUID | None = None) -> bool:
        """Link a member profile to an actual User account."""
        stmt = (
            update(Member)
            .where(
                Member.id == member_id, Member.tenant_id == self.tenant_id, Member.is_deleted == False  # noqa: E712
            )
            .values(user_id=user_id, updated_by=updated_by)
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    # ── Delete ───────────────────────────────────────────────────────────

    async def soft_delete(self, member_id: UUID, deleted_by: UUID | None = None) -> bool:
        stmt = (
            update(Member)
            .where(
                Member.id == member_id, Member.tenant_id == self.tenant_id, Member.is_deleted == False  # noqa: E712
            )
            .values(is_deleted=True, status="inactive", updated_by=deleted_by)
        )
        # Note: In a real app we might also need to handle the deleted_at timestamp,
        # but the base model might rely on application logic or DB triggers for it.
        # Since we use `BaseModel` we should ideally set it via object manipulation or literal values.
        from datetime import UTC, datetime

        stmt = stmt.values(deleted_at=datetime.now(UTC))

        result = await self._session.execute(stmt)
        return result.rowcount > 0
