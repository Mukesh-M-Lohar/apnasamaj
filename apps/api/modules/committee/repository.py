"""
ApnaSamaj – Committee Repository

Database operations for committees and committee members.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import Select, delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.modules.committee.models import Committee, CommitteeMember
from apps.api.modules.member.models import Member


class CommitteeRepository:
    """Handles committee DB operations scoped to a tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self._session = session
        self.tenant_id = tenant_id

    def _base_query(self) -> Select:
        return select(Committee).where(
            Committee.tenant_id == self.tenant_id,
            Committee.is_deleted == False,  # noqa: E712
        )

    # ── Create ───────────────────────────────────────────────────────────

    async def create(self, data: dict[str, Any], created_by: UUID | None = None) -> Committee:
        committee = Committee(
            tenant_id=self.tenant_id,
            created_by=created_by,
            updated_by=created_by,
            **data,
        )
        self._session.add(committee)
        await self._session.flush()
        await self._session.refresh(committee)
        return committee

    # ── Read ─────────────────────────────────────────────────────────────

    async def get_by_id(self, committee_id: UUID) -> Committee | None:
        stmt = self._base_query().where(Committee.id == committee_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_paginated(
        self,
        offset: int = 0,
        limit: int = 20,
        search: str | None = None,
        status: str | None = None,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> tuple[list[Committee], int]:
        stmt = self._base_query()
        count_stmt = (
            select(func.count())
            .select_from(Committee)
            .where(
                Committee.tenant_id == self.tenant_id,
                Committee.is_deleted == False,  # noqa: E712
            )
        )

        if status:
            stmt = stmt.where(Committee.status == status)
            count_stmt = count_stmt.where(Committee.status == status)

        if search:
            search_filter = f"%{search}%"
            stmt = stmt.where(Committee.name.ilike(search_filter))
            count_stmt = count_stmt.where(Committee.name.ilike(search_filter))

        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        sort_column = getattr(Committee, sort_by, Committee.name)
        stmt = stmt.order_by(sort_column.desc() if sort_order == "desc" else sort_column.asc())
        stmt = stmt.offset(offset).limit(limit)

        result = await self._session.execute(stmt)
        committees = list(result.scalars().all())

        return committees, total

    # ── Update ───────────────────────────────────────────────────────────

    async def update(
        self, committee_id: UUID, data: dict[str, Any], updated_by: UUID | None = None
    ) -> Committee | None:
        committee = await self.get_by_id(committee_id)
        if not committee:
            return None

        for key, value in data.items():
            if value is not None and hasattr(committee, key):
                setattr(committee, key, value)

        if updated_by:
            committee.updated_by = updated_by

        await self._session.flush()
        await self._session.refresh(committee)
        return committee

    # ── Delete ───────────────────────────────────────────────────────────

    async def soft_delete(self, committee_id: UUID, deleted_by: UUID | None = None) -> bool:
        stmt = (
            update(Committee)
            .where(
                Committee.id == committee_id,
                Committee.tenant_id == self.tenant_id,
                Committee.is_deleted == False,  # noqa: E712
            )
            .values(is_deleted=True, updated_by=deleted_by)
        )
        from datetime import UTC, datetime

        stmt = stmt.values(deleted_at=datetime.now(UTC))

        result = await self._session.execute(stmt)
        return result.rowcount > 0

    # ── Committee Members (Junction) ─────────────────────────────────────

    async def get_committee_members(self, committee_id: UUID) -> list[CommitteeMember]:
        """Fetch all members linked to a committee, along with their member profiles."""
        stmt = (
            select(CommitteeMember, Member)
            .join(Member, CommitteeMember.member_id == Member.id)
            .where(
                CommitteeMember.committee_id == committee_id,
                CommitteeMember.tenant_id == self.tenant_id,
                CommitteeMember.is_deleted == False,  # noqa: E712
            )
        )
        result = await self._session.execute(stmt)

        members_linked = []
        for cm, m in result:
            cm.member_obj = m
            members_linked.append(cm)

        return members_linked

    async def add_member(
        self,
        committee_id: UUID,
        member_id: UUID,
        position: str,
        responsibilities: str | None = None,
        joined_date: Any | None = None,
        left_date: Any | None = None,
        status: str = "active",
        created_by: UUID | None = None,
    ) -> CommitteeMember:
        """Add a member to the committee."""
        cm = CommitteeMember(
            tenant_id=self.tenant_id,
            committee_id=committee_id,
            member_id=member_id,
            position=position,
            responsibilities=responsibilities,
            joined_date=joined_date,
            left_date=left_date,
            status=status,
            created_by=created_by,
        )
        self._session.add(cm)
        await self._session.flush()
        await self._session.refresh(cm)
        return cm

    async def remove_member(self, committee_id: UUID, member_id: UUID) -> bool:
        """Remove a member from the committee (hard delete the junction row)."""
        stmt = delete(CommitteeMember).where(
            CommitteeMember.committee_id == committee_id,
            CommitteeMember.member_id == member_id,
        )
        result = await self._session.execute(stmt)
        return result.rowcount > 0
