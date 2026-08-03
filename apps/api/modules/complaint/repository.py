"""
ApnaSamaj – Complaint Repository

Database operations for handling member complaints/tickets.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import Select, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.modules.complaint.models import Complaint, ComplaintStatus


class ComplaintRepository:
    """Handles complaint DB operations scoped to a tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self._session = session
        self.tenant_id = tenant_id

    def _base_query(self) -> Select:
        return select(Complaint).where(
            Complaint.tenant_id == self.tenant_id,
            Complaint.is_deleted == False,  # noqa: E712
        )

    # ── Create ───────────────────────────────────────────────────────────

    async def create(self, data: dict[str, Any], created_by: UUID | None = None) -> Complaint:
        complaint = Complaint(
            tenant_id=self.tenant_id,
            created_by=created_by,
            updated_by=created_by,
            **data,
        )
        self._session.add(complaint)
        await self._session.flush()
        await self._session.refresh(complaint)
        return complaint

    # ── Read ─────────────────────────────────────────────────────────────

    async def get_by_id(self, complaint_id: UUID) -> Complaint | None:
        stmt = self._base_query().where(Complaint.id == complaint_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_paginated(
        self,
        offset: int = 0,
        limit: int = 20,
        status: ComplaintStatus | None = None,
        reporter_id: UUID | None = None,
        committee_id: UUID | None = None,
    ) -> tuple[list[Complaint], int]:
        stmt = self._base_query()
        count_stmt = (
            select(func.count())
            .select_from(Complaint)
            .where(
                Complaint.tenant_id == self.tenant_id,
                Complaint.is_deleted == False,  # noqa: E712
            )
        )

        if status:
            stmt = stmt.where(Complaint.status == status)
            count_stmt = count_stmt.where(Complaint.status == status)

        if reporter_id:
            stmt = stmt.where(Complaint.reporter_id == reporter_id)
            count_stmt = count_stmt.where(Complaint.reporter_id == reporter_id)

        if committee_id:
            stmt = stmt.where(Complaint.assigned_committee_id == committee_id)
            count_stmt = count_stmt.where(Complaint.assigned_committee_id == committee_id)

        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = stmt.order_by(Complaint.created_at.desc())
        stmt = stmt.offset(offset).limit(limit)

        result = await self._session.execute(stmt)
        complaints = list(result.scalars().all())

        return complaints, total

    # ── Update ───────────────────────────────────────────────────────────

    async def update(
        self, complaint_id: UUID, data: dict[str, Any], updated_by: UUID | None = None
    ) -> Complaint | None:
        complaint = await self.get_by_id(complaint_id)
        if not complaint:
            return None

        for key, value in data.items():
            if value is not None and hasattr(complaint, key):
                setattr(complaint, key, value)

        if updated_by:
            complaint.updated_by = updated_by

        await self._session.flush()
        await self._session.refresh(complaint)
        return complaint

    # ── Delete ───────────────────────────────────────────────────────────

    async def soft_delete(self, complaint_id: UUID, deleted_by: UUID | None = None) -> bool:
        from datetime import UTC, datetime

        stmt = (
            update(Complaint)
            .where(
                Complaint.id == complaint_id,
                Complaint.tenant_id == self.tenant_id,
                Complaint.is_deleted == False,  # noqa: E712
            )
            .values(is_deleted=True, updated_by=deleted_by, deleted_at=datetime.now(UTC))
        )

        result = await self._session.execute(stmt)
        return result.rowcount > 0
