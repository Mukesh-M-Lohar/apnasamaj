"""
ApnaSamaj – Facility Service

Business logic for managing facilities and executing collision-checked bookings.
"""

from __future__ import annotations

import logging
import math
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from apps.api.core.exceptions import NotFoundException
from apps.api.modules.facility.repository import FacilityRepository
from apps.api.modules.facility.schemas import (
    FacilityBookingCreateSchema,
    FacilityBookingResponse,
    FacilityBookingUpdateSchema,
    FacilityCreateSchema,
    FacilityResponse,
    FacilityUpdateSchema,
)

logger = logging.getLogger(__name__)


class FacilityService:
    """Business logic for facility booking."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self._repo = FacilityRepository(session, tenant_id)
        self.tenant_id = tenant_id

    # ── Facilities ───────────────────────────────────────────────────────

    async def create_facility(
        self,
        data: FacilityCreateSchema,
        created_by: UUID | None = None,
    ) -> FacilityResponse:
        facility = await self._repo.create_facility(
            data=data.model_dump(exclude_none=True),
            created_by=created_by,
        )
        logger.info("Facility created: %s", facility.name)
        return FacilityResponse.model_validate(facility)

    async def get_facility(self, facility_id: UUID) -> FacilityResponse:
        facility = await self._repo.get_facility_by_id(facility_id)
        if not facility:
            raise NotFoundException("Facility", str(facility_id))
        return FacilityResponse.model_validate(facility)

    async def list_facilities(
        self,
        page: int = 1,
        per_page: int = 20,
    ) -> dict[str, Any]:
        offset = (page - 1) * per_page
        facilities, total = await self._repo.get_all_facilities(offset=offset, limit=per_page)

        total_pages = math.ceil(total / per_page) if per_page > 0 else 0
        items = [FacilityResponse.model_validate(f) for f in facilities]

        return {
            "items": items,
            "meta": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            },
        }

    async def update_facility(
        self,
        facility_id: UUID,
        data: FacilityUpdateSchema,
        updated_by: UUID | None = None,
    ) -> FacilityResponse:
        facility = await self._repo.update_facility(
            facility_id=facility_id,
            data=data.model_dump(exclude_unset=True),
            updated_by=updated_by,
        )
        if not facility:
            raise NotFoundException("Facility", str(facility_id))
        return FacilityResponse.model_validate(facility)

    async def delete_facility(self, facility_id: UUID, deleted_by: UUID | None = None) -> dict:
        success = await self._repo.soft_delete_facility(facility_id, deleted_by)
        if not success:
            raise NotFoundException("Facility", str(facility_id))
        return {"message": "Facility deleted successfully"}

    # ── Bookings ─────────────────────────────────────────────────────────

    async def book_facility(
        self, 
        facility_id: UUID, 
        data: FacilityBookingCreateSchema, 
        booked_by: UUID
    ) -> FacilityBookingResponse:
        """Create a booking ensuring no double-booking."""
        facility = await self._repo.get_facility_by_id(facility_id)
        if not facility or not facility.is_active:
            raise NotFoundException("Facility", str(facility_id))

        # Check collisions
        is_available = await self._repo.check_availability(
            facility_id=facility_id,
            start_time=data.start_time,
            end_time=data.end_time
        )
        if not is_available:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Facility is already booked during this time slot."
            )

        booking = await self._repo.create_booking(
            facility_id=facility_id,
            data={"start_time": data.start_time, "end_time": data.end_time, "booked_by_id": booked_by},
            created_by=booked_by,
        )
        return FacilityBookingResponse.model_validate(booking)

    async def update_booking(
        self,
        booking_id: UUID,
        data: FacilityBookingUpdateSchema,
        updated_by: UUID | None = None,
    ) -> FacilityBookingResponse:
        booking = await self._repo.update_booking(
            booking_id=booking_id,
            data=data.model_dump(exclude_unset=True),
            updated_by=updated_by,
        )
        if not booking:
            raise NotFoundException("FacilityBooking", str(booking_id))
        return FacilityBookingResponse.model_validate(booking)

    async def get_facility_bookings(self, facility_id: UUID) -> list[FacilityBookingResponse]:
        bookings = await self._repo.get_bookings_for_facility(facility_id)
        return [FacilityBookingResponse.model_validate(b) for b in bookings]
