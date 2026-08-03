"""
ApnaSamaj – Volunteer Repository

Database operations for volunteers and event assignments.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import Select, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.modules.volunteer.models import Volunteer, VolunteerAssignment


class VolunteerRepository:
    """Handles volunteer DB operations scoped to a tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self._session = session
        self.tenant_id = tenant_id

    def _base_query(self) -> Select:
        return select(Volunteer).where(
            Volunteer.tenant_id == self.tenant_id,
            Volunteer.is_deleted == False,  # noqa: E712
        )

    # ── Create ───────────────────────────────────────────────────────────

    async def create(self, data: dict[str, Any], created_by: UUID | None = None) -> Volunteer:
        volunteer = Volunteer(
            tenant_id=self.tenant_id,
            created_by=created_by,
            updated_by=created_by,
            **data,
        )
        self._session.add(volunteer)
        await self._session.flush()
        await self._session.refresh(volunteer)
        return volunteer

    # ── Read ─────────────────────────────────────────────────────────────

    async def get_by_id(self, volunteer_id: UUID) -> Volunteer | None:
        stmt = self._base_query().where(Volunteer.id == volunteer_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_paginated(
        self,
        offset: int = 0,
        limit: int = 20,
        status: str | None = None,
        skill: str | None = None,
        availability: str | None = None,
        sort_by: str = "total_hours",
        sort_order: str = "desc",
    ) -> tuple[list[Volunteer], int]:
        stmt = self._base_query()
        count_stmt = (
            select(func.count())
            .select_from(Volunteer)
            .where(
                Volunteer.tenant_id == self.tenant_id,
                Volunteer.is_deleted == False,  # noqa: E712
            )
        )

        if status:
            stmt = stmt.where(Volunteer.status == status)
            count_stmt = count_stmt.where(Volunteer.status == status)

        if availability:
            stmt = stmt.where(Volunteer.availability == availability)
            count_stmt = count_stmt.where(Volunteer.availability == availability)

        if skill:
            # Query JSONB array for the specific skill using Postgres ? operator wrapper
            # In SQLAlchemy with asyncpg, we use .op("?"). Since JSONB isn't strictly strongly-typed here without cast, we use contains.
            # Assuming skills is a list of strings: '["cooking", "usher"]'
            stmt = stmt.where(Volunteer.skills.contains([skill]))
            count_stmt = count_stmt.where(Volunteer.skills.contains([skill]))

        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        sort_column = getattr(Volunteer, sort_by, Volunteer.total_hours)
        stmt = stmt.order_by(sort_column.desc() if sort_order == "desc" else sort_column.asc())
        stmt = stmt.offset(offset).limit(limit)

        result = await self._session.execute(stmt)
        volunteers = list(result.scalars().all())

        return volunteers, total

    # ── Update ───────────────────────────────────────────────────────────

    async def update(
        self, volunteer_id: UUID, data: dict[str, Any], updated_by: UUID | None = None
    ) -> Volunteer | None:
        volunteer = await self.get_by_id(volunteer_id)
        if not volunteer:
            return None

        for key, value in data.items():
            if value is not None and hasattr(volunteer, key):
                setattr(volunteer, key, value)

        if updated_by:
            volunteer.updated_by = updated_by

        await self._session.flush()
        await self._session.refresh(volunteer)
        return volunteer

    # ── Delete ───────────────────────────────────────────────────────────

    async def soft_delete(self, volunteer_id: UUID, deleted_by: UUID | None = None) -> bool:
        stmt = (
            update(Volunteer)
            .where(
                Volunteer.id == volunteer_id,
                Volunteer.tenant_id == self.tenant_id,
                Volunteer.is_deleted == False,  # noqa: E712
            )
            .values(is_deleted=True, updated_by=deleted_by)
        )
        from datetime import UTC, datetime

        stmt = stmt.values(deleted_at=datetime.now(UTC))

        result = await self._session.execute(stmt)
        return result.rowcount > 0

    # ── Assignments ──────────────────────────────────────────────────────

    async def assign_volunteer(
        self,
        volunteer_id: UUID,
        event_id: UUID,
        role: str | None = None,
        created_by: UUID | None = None,
    ) -> VolunteerAssignment:
        assignment = VolunteerAssignment(
            tenant_id=self.tenant_id,
            volunteer_id=volunteer_id,
            event_id=event_id,
            role=role,
            created_by=created_by,
        )
        self._session.add(assignment)
        await self._session.flush()
        await self._session.refresh(assignment)
        return assignment

    async def get_assignment(self, assignment_id: UUID) -> VolunteerAssignment | None:
        stmt = select(VolunteerAssignment).where(
            VolunteerAssignment.id == assignment_id,
            VolunteerAssignment.tenant_id == self.tenant_id,
            VolunteerAssignment.is_deleted == False,  # noqa: E712
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_assignments_for_volunteer(self, volunteer_id: UUID) -> list[VolunteerAssignment]:
        stmt = (
            select(VolunteerAssignment)
            .where(
                VolunteerAssignment.volunteer_id == volunteer_id,
                VolunteerAssignment.tenant_id == self.tenant_id,
                VolunteerAssignment.is_deleted == False,  # noqa: E712
            )
            .order_by(VolunteerAssignment.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update_assignment(
        self, assignment_id: UUID, data: dict[str, Any], updated_by: UUID | None = None
    ) -> VolunteerAssignment | None:
        assignment = await self.get_assignment(assignment_id)
        if not assignment:
            return None

        for key, value in data.items():
            if value is not None and hasattr(assignment, key):
                setattr(assignment, key, value)

        if updated_by:
            assignment.updated_by = updated_by

        await self._session.flush()
        await self._session.refresh(assignment)
        return assignment

    async def update_volunteer_stats(self, volunteer_id: UUID) -> None:
        """Recalculate total hours and total events attended."""
        stmt = select(
            func.sum(VolunteerAssignment.hours).label("total_hours"),
            func.count(VolunteerAssignment.id).label("total_events"),
        ).where(
            VolunteerAssignment.volunteer_id == volunteer_id,
            VolunteerAssignment.attended == True,  # noqa: E712
            VolunteerAssignment.is_deleted == False,  # noqa: E712
        )
        result = await self._session.execute(stmt)
        row = result.first()

        hours = row.total_hours or 0
        events_count = row.total_events or 0

        update_stmt = (
            update(Volunteer).where(Volunteer.id == volunteer_id).values(total_hours=hours, total_events=events_count)
        )
        await self._session.execute(update_stmt)
        await self._session.flush()
