"""
ApnaSamaj – Family Repository

Database operations for families and linking family members.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import Select, delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.modules.family.models import Family, FamilyMember
from apps.api.modules.member.models import Member


class FamilyRepository:
    """Handles family DB operations scoped to a tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self._session = session
        self.tenant_id = tenant_id

    def _base_query(self) -> Select:
        return select(Family).where(
            Family.tenant_id == self.tenant_id,
            Family.is_deleted == False,  # noqa: E712
        )

    # ── Create ───────────────────────────────────────────────────────────

    async def create(self, data: dict[str, Any], created_by: UUID | None = None) -> Family:
        family = Family(
            tenant_id=self.tenant_id,
            created_by=created_by,
            updated_by=created_by,
            **data,
        )
        self._session.add(family)
        await self._session.flush()
        await self._session.refresh(family)
        return family

    # ── Read ─────────────────────────────────────────────────────────────

    async def get_by_id(self, family_id: UUID) -> Family | None:
        stmt = self._base_query().where(Family.id == family_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_paginated(
        self,
        offset: int = 0,
        limit: int = 20,
        search: str | None = None,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> tuple[list[Family], int]:
        stmt = self._base_query()
        count_stmt = (
            select(func.count())
            .select_from(Family)
            .where(
                Family.tenant_id == self.tenant_id,
                Family.is_deleted == False,  # noqa: E712
            )
        )

        if search:
            search_filter = f"%{search}%"
            stmt = stmt.where(Family.name.ilike(search_filter))
            count_stmt = count_stmt.where(Family.name.ilike(search_filter))

        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        sort_column = getattr(Family, sort_by, Family.name)
        stmt = stmt.order_by(sort_column.desc() if sort_order == "desc" else sort_column.asc())
        stmt = stmt.offset(offset).limit(limit)

        result = await self._session.execute(stmt)
        families = list(result.scalars().all())

        return families, total

    # ── Update ───────────────────────────────────────────────────────────

    async def update(self, family_id: UUID, data: dict[str, Any], updated_by: UUID | None = None) -> Family | None:
        family = await self.get_by_id(family_id)
        if not family:
            return None

        for key, value in data.items():
            if value is not None and hasattr(family, key):
                setattr(family, key, value)

        if updated_by:
            family.updated_by = updated_by

        await self._session.flush()
        await self._session.refresh(family)
        return family

    # ── Delete ───────────────────────────────────────────────────────────

    async def soft_delete(self, family_id: UUID, deleted_by: UUID | None = None) -> bool:
        stmt = (
            update(Family)
            .where(
                Family.id == family_id, Family.tenant_id == self.tenant_id, Family.is_deleted == False  # noqa: E712
            )
            .values(is_deleted=True, updated_by=deleted_by)
        )
        from datetime import UTC, datetime

        stmt = stmt.values(deleted_at=datetime.now(UTC))

        result = await self._session.execute(stmt)
        return result.rowcount > 0

    # ── Family Members (Junction) ────────────────────────────────────────

    async def get_family_members(self, family_id: UUID) -> list[FamilyMember]:
        """Fetch all family members linked to a family, along with the member profile."""
        # Note: In a real app we'd configure a relationship() on the model.
        # Here we manually join/load them to keep models clean if no relationship is defined.
        # But we must return the actual Member data too.
        # Let's use a standard join.
        stmt = (
            select(FamilyMember, Member)
            .join(Member, FamilyMember.member_id == Member.id)
            .where(
                FamilyMember.family_id == family_id,
                FamilyMember.tenant_id == self.tenant_id,
                FamilyMember.is_deleted == False,  # noqa: E712
            )
        )
        result = await self._session.execute(stmt)

        # We'll attach the Member object directly to the FamilyMember for easy access
        members_linked = []
        for fm, m in result:
            fm.member_obj = m
            members_linked.append(fm)

        return members_linked

    async def add_member(
        self,
        family_id: UUID,
        member_id: UUID,
        relationship_type: str,
        related_to_member_id: UUID | None = None,
        generation: int | None = None,
        created_by: UUID | None = None,
    ) -> FamilyMember:
        """Add a member to the family."""
        fm = FamilyMember(
            tenant_id=self.tenant_id,
            family_id=family_id,
            member_id=member_id,
            relationship_type=relationship_type,
            related_to_member_id=related_to_member_id,
            generation=generation,
            created_by=created_by,
        )
        self._session.add(fm)

        # Also update the member's family_id
        await self._session.execute(update(Member).where(Member.id == member_id).values(family_id=family_id))

        await self._session.flush()
        await self._session.refresh(fm)
        return fm

    async def remove_member(self, family_id: UUID, member_id: UUID) -> bool:
        """Remove a member from the family (hard delete the junction row)."""
        stmt = delete(FamilyMember).where(
            FamilyMember.family_id == family_id,
            FamilyMember.member_id == member_id,
        )
        result = await self._session.execute(stmt)

        # Unlink family_id on the member
        if result.rowcount > 0:
            await self._session.execute(update(Member).where(Member.id == member_id).values(family_id=None))

        return result.rowcount > 0
