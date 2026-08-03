"""
ApnaSamaj – Event Service

Business logic for event management, registrations (RSVPs), and capacity checks.
"""

from __future__ import annotations

import logging
import math
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.exceptions import AppException, NotFoundException
from apps.api.modules.event.repository import EventRepository
from apps.api.modules.event.schemas import (
    EventCheckInSchema,
    EventCreateSchema,
    EventRegistrationResponse,
    EventRegistrationSchema,
    EventResponse,
    EventUpdateSchema,
)

logger = logging.getLogger(__name__)


class EventService:
    """Business logic for event management."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self._repo = EventRepository(session, tenant_id)
        self.tenant_id = tenant_id

    # ── Create ───────────────────────────────────────────────────────────

    async def create_event(
        self,
        data: EventCreateSchema,
        created_by: UUID | None = None,
    ) -> EventResponse:
        """Create a new event."""
        event = await self._repo.create(
            data=data.model_dump(exclude_none=True),
            created_by=created_by,
        )
        logger.info("Event created: %s", event.title)
        return EventResponse.model_validate(event)

    # ── Read ─────────────────────────────────────────────────────────────

    async def get_event(self, event_id: UUID) -> EventResponse:
        """Get a specific event."""
        event = await self._repo.get_by_id(event_id)
        if not event:
            raise NotFoundException("Event", str(event_id))
        return EventResponse.model_validate(event)

    async def list_events(
        self,
        page: int = 1,
        per_page: int = 20,
        status: str | None = None,
        event_type: str | None = None,
        search: str | None = None,
        sort_by: str = "start_date",
        sort_order: str = "asc",
    ) -> dict[str, Any]:
        """List events with pagination."""
        offset = (page - 1) * per_page

        events, total = await self._repo.get_all_paginated(
            offset=offset,
            limit=per_page,
            status=status,
            event_type=event_type,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        total_pages = math.ceil(total / per_page) if per_page > 0 else 0
        items = [EventResponse.model_validate(e) for e in events]

        return {
            "items": items,
            "meta": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            },
        }

    # ── Update ───────────────────────────────────────────────────────────

    async def update_event(
        self,
        event_id: UUID,
        data: EventUpdateSchema,
        updated_by: UUID | None = None,
    ) -> EventResponse:
        """Update an event."""
        event = await self._repo.update(
            event_id=event_id,
            data=data.model_dump(exclude_unset=True),
            updated_by=updated_by,
        )
        if not event:
            raise NotFoundException("Event", str(event_id))

        return EventResponse.model_validate(event)

    # ── Delete ───────────────────────────────────────────────────────────

    async def delete_event(self, event_id: UUID, deleted_by: UUID | None = None) -> dict:
        """Soft-delete an event."""
        success = await self._repo.soft_delete(event_id, deleted_by)
        if not success:
            raise NotFoundException("Event", str(event_id))
        logger.info("Event soft-deleted: %s by %s", event_id, deleted_by)
        return {"message": "Event deleted successfully"}

    # ── Registration & Attendance ────────────────────────────────────────

    async def register_member(
        self, event_id: UUID, data: EventRegistrationSchema, created_by: UUID | None = None
    ) -> EventRegistrationResponse:
        """Register a member for an event (RSVP)."""
        event = await self._repo.get_by_id(event_id)
        if not event:
            raise NotFoundException("Event", str(event_id))

        if not event.is_registration_open:
            raise AppException("Registration is closed for this event")

        if event.registration_deadline and event.registration_deadline < datetime.now(UTC):
            raise AppException("Registration deadline has passed")

        if event.max_attendees:
            current_count = await self._repo.get_registration_count(event_id)
            if current_count + 1 + data.guests > event.max_attendees:
                raise AppException("Event is at full capacity")

        reg = await self._repo.register_member(
            event_id=event_id,
            member_id=data.member_id,
            guests=data.guests,
            notes=data.notes,
            created_by=created_by,
        )
        return EventRegistrationResponse.model_validate(reg)

    async def check_in_member(
        self, event_id: UUID, data: EventCheckInSchema, updated_by: UUID | None = None
    ) -> EventRegistrationResponse:
        """Mark a member as attended."""
        reg = await self._repo.mark_attendance(
            event_id=event_id, member_id=data.member_id, method=data.check_in_method, updated_by=updated_by
        )
        if not reg:
            raise NotFoundException("EventRegistration", f"{event_id}-{data.member_id}")

        return EventRegistrationResponse.model_validate(reg)

    async def get_attendees(self, event_id: UUID) -> list[EventRegistrationResponse]:
        """Fetch all registrations for an event."""
        regs = await self._repo.get_attendees(event_id)
        return [EventRegistrationResponse.model_validate(r) for r in regs]
