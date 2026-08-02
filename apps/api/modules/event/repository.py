"""
ApnaSamaj – Event Repository

Database operations for events and attendee registrations.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID
from datetime import datetime, UTC

from sqlalchemy import Select, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.modules.event.models import Event, EventRegistration


class EventRepository:
    """Handles event DB operations scoped to a tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self._session = session
        self.tenant_id = tenant_id

    def _base_query(self) -> Select:
        return select(Event).where(
            Event.tenant_id == self.tenant_id,
            Event.is_deleted == False,  # noqa: E712
        )

    # ── Create ───────────────────────────────────────────────────────────

    async def create(self, data: dict[str, Any], created_by: UUID | None = None) -> Event:
        event = Event(
            tenant_id=self.tenant_id,
            created_by=created_by,
            updated_by=created_by,
            **data,
        )
        self._session.add(event)
        await self._session.flush()
        await self._session.refresh(event)
        return event

    # ── Read ─────────────────────────────────────────────────────────────

    async def get_by_id(self, event_id: UUID) -> Event | None:
        stmt = self._base_query().where(Event.id == event_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_paginated(
        self,
        offset: int = 0,
        limit: int = 20,
        status: str | None = None,
        event_type: str | None = None,
        search: str | None = None,
        sort_by: str = "start_date",
        sort_order: str = "asc",
    ) -> tuple[list[Event], int]:
        stmt = self._base_query()
        count_stmt = select(func.count()).select_from(Event).where(
            Event.tenant_id == self.tenant_id,
            Event.is_deleted == False,  # noqa: E712
        )

        if status:
            stmt = stmt.where(Event.status == status)
            count_stmt = count_stmt.where(Event.status == status)
            
        if event_type:
            stmt = stmt.where(Event.event_type == event_type)
            count_stmt = count_stmt.where(Event.event_type == event_type)
            
        if search:
            search_filter = f"%{search}%"
            stmt = stmt.where(Event.title.ilike(search_filter))
            count_stmt = count_stmt.where(Event.title.ilike(search_filter))

        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        sort_column = getattr(Event, sort_by, Event.start_date)
        stmt = stmt.order_by(sort_column.desc() if sort_order == "desc" else sort_column.asc())
        stmt = stmt.offset(offset).limit(limit)

        result = await self._session.execute(stmt)
        events = list(result.scalars().all())

        return events, total

    # ── Update ───────────────────────────────────────────────────────────

    async def update(
        self, event_id: UUID, data: dict[str, Any], updated_by: UUID | None = None
    ) -> Event | None:
        event = await self.get_by_id(event_id)
        if not event:
            return None

        for key, value in data.items():
            if value is not None and hasattr(event, key):
                setattr(event, key, value)

        if updated_by:
            event.updated_by = updated_by

        await self._session.flush()
        await self._session.refresh(event)
        return event

    # ── Delete ───────────────────────────────────────────────────────────

    async def soft_delete(self, event_id: UUID, deleted_by: UUID | None = None) -> bool:
        stmt = (
            update(Event)
            .where(
                Event.id == event_id,
                Event.tenant_id == self.tenant_id,
                Event.is_deleted == False  # noqa: E712
            )
            .values(is_deleted=True, updated_by=deleted_by, deleted_at=datetime.now(UTC))
        )
        
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    # ── Registration & Attendance ────────────────────────────────────────

    async def get_registration(self, event_id: UUID, member_id: UUID) -> EventRegistration | None:
        stmt = select(EventRegistration).where(
            EventRegistration.event_id == event_id,
            EventRegistration.member_id == member_id,
            EventRegistration.tenant_id == self.tenant_id,
            EventRegistration.is_deleted == False  # noqa: E712
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
        
    async def get_registration_count(self, event_id: UUID) -> int:
        stmt = select(func.count()).select_from(EventRegistration).where(
            EventRegistration.event_id == event_id,
            EventRegistration.status == "registered",
            EventRegistration.is_deleted == False  # noqa: E712
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def register_member(
        self,
        event_id: UUID,
        member_id: UUID,
        guests: int = 0,
        notes: str | None = None,
        created_by: UUID | None = None,
    ) -> EventRegistration:
        """Upsert a registration for an event."""
        existing = await self.get_registration(event_id, member_id)
        if existing:
            existing.guests = guests
            existing.notes = notes
            existing.status = "registered"
            existing.updated_by = created_by
            reg = existing
        else:
            reg = EventRegistration(
                tenant_id=self.tenant_id,
                event_id=event_id,
                member_id=member_id,
                guests=guests,
                notes=notes,
                status="registered",
                created_by=created_by,
            )
            self._session.add(reg)
            
        await self._session.flush()
        await self._session.refresh(reg)
        return reg

    async def mark_attendance(
        self, 
        event_id: UUID, 
        member_id: UUID, 
        method: str = "manual",
        updated_by: UUID | None = None
    ) -> EventRegistration | None:
        reg = await self.get_registration(event_id, member_id)
        if not reg:
            return None
            
        reg.status = "attended"
        reg.checked_in_at = datetime.now(UTC)
        reg.check_in_method = method
        reg.updated_by = updated_by
        
        await self._session.flush()
        await self._session.refresh(reg)
        return reg

    async def get_attendees(self, event_id: UUID) -> list[EventRegistration]:
        stmt = select(EventRegistration).where(
            EventRegistration.event_id == event_id,
            EventRegistration.tenant_id == self.tenant_id,
            EventRegistration.is_deleted == False  # noqa: E712
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
