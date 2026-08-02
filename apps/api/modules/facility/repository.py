"""
ApnaSamaj – Facility Repository

Database operations for handling facility CRUD and booking collision detection.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Select, func, select, update, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.modules.facility.models import BookingStatus, Facility, FacilityBooking


class FacilityRepository:
    """Handles facility and booking DB operations scoped to a tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self._session = session
        self.tenant_id = tenant_id

    # ── Facility CRUD ────────────────────────────────────────────────────

    def _base_facility_query(self) -> Select:
        return select(Facility).where(
            Facility.tenant_id == self.tenant_id,
            Facility.is_deleted == False,  # noqa: E712
        )

    async def create_facility(self, data: dict[str, Any], created_by: UUID | None = None) -> Facility:
        facility = Facility(
            tenant_id=self.tenant_id,
            created_by=created_by,
            updated_by=created_by,
            **data,
        )
        self._session.add(facility)
        await self._session.flush()
        await self._session.refresh(facility)
        return facility

    async def get_facility_by_id(self, facility_id: UUID) -> Facility | None:
        stmt = self._base_facility_query().where(Facility.id == facility_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_facilities(
        self,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Facility], int]:
        stmt = self._base_facility_query()
        count_stmt = select(func.count()).select_from(Facility).where(
            Facility.tenant_id == self.tenant_id,
            Facility.is_deleted == False,  # noqa: E712
        )

        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = stmt.order_by(Facility.name.asc())
        stmt = stmt.offset(offset).limit(limit)

        result = await self._session.execute(stmt)
        facilities = list(result.scalars().all())

        return facilities, total

    async def update_facility(
        self, facility_id: UUID, data: dict[str, Any], updated_by: UUID | None = None
    ) -> Facility | None:
        facility = await self.get_facility_by_id(facility_id)
        if not facility:
            return None

        for key, value in data.items():
            if value is not None and hasattr(facility, key):
                setattr(facility, key, value)

        if updated_by:
            facility.updated_by = updated_by

        await self._session.flush()
        await self._session.refresh(facility)
        return facility

    async def soft_delete_facility(self, facility_id: UUID, deleted_by: UUID | None = None) -> bool:
        from datetime import datetime, UTC
        stmt = (
            update(Facility)
            .where(
                Facility.id == facility_id,
                Facility.tenant_id == self.tenant_id,
                Facility.is_deleted == False  # noqa: E712
            )
            .values(
                is_deleted=True, 
                updated_by=deleted_by,
                deleted_at=datetime.now(UTC)
            )
        )
        
        result = await self._session.execute(stmt)
        return result.rowcount > 0

    # ── Booking & Collision Detection ────────────────────────────────────

    async def check_availability(self, facility_id: UUID, start_time: datetime, end_time: datetime) -> bool:
        """
        Check if the facility is available for the given time slot.
        Returns True if available (no collisions), False otherwise.
        """
        # Logic: A collision exists if an active booking intersects with [start_time, end_time)
        # Booking intersects if: booking.start_time < new.end_time AND booking.end_time > new.start_time
        stmt = select(FacilityBooking).where(
            FacilityBooking.facility_id == facility_id,
            FacilityBooking.tenant_id == self.tenant_id,
            FacilityBooking.is_deleted == False,  # noqa: E712
            FacilityBooking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
            FacilityBooking.start_time < end_time,
            FacilityBooking.end_time > start_time
        )
        result = await self._session.execute(stmt)
        collision = result.first()
        return collision is None

    async def create_booking(self, facility_id: UUID, data: dict[str, Any], created_by: UUID | None = None) -> FacilityBooking:
        booking = FacilityBooking(
            tenant_id=self.tenant_id,
            facility_id=facility_id,
            created_by=created_by,
            updated_by=created_by,
            **data,
        )
        self._session.add(booking)
        await self._session.flush()
        await self._session.refresh(booking)
        return booking

    async def get_booking_by_id(self, booking_id: UUID) -> FacilityBooking | None:
        stmt = select(FacilityBooking).where(
            FacilityBooking.id == booking_id,
            FacilityBooking.tenant_id == self.tenant_id,
            FacilityBooking.is_deleted == False  # noqa: E712
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_booking(
        self, booking_id: UUID, data: dict[str, Any], updated_by: UUID | None = None
    ) -> FacilityBooking | None:
        booking = await self.get_booking_by_id(booking_id)
        if not booking:
            return None

        for key, value in data.items():
            if value is not None and hasattr(booking, key):
                setattr(booking, key, value)

        if updated_by:
            booking.updated_by = updated_by

        await self._session.flush()
        await self._session.refresh(booking)
        return booking

    async def get_bookings_for_facility(self, facility_id: UUID) -> list[FacilityBooking]:
        stmt = select(FacilityBooking).where(
            FacilityBooking.facility_id == facility_id,
            FacilityBooking.tenant_id == self.tenant_id,
            FacilityBooking.is_deleted == False  # noqa: E712
        ).order_by(FacilityBooking.start_time.asc())
        
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
