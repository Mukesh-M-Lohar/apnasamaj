"""
ApnaSamaj – Volunteer Service

Business logic for managing volunteers and tracking their hours.
"""

from __future__ import annotations

import logging
import math
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.exceptions import NotFoundException
from apps.api.modules.volunteer.repository import VolunteerRepository
from apps.api.modules.volunteer.schemas import (
    VolunteerAssignmentCreateSchema,
    VolunteerAssignmentResponse,
    VolunteerAssignmentUpdateSchema,
    VolunteerCreateSchema,
    VolunteerResponse,
    VolunteerUpdateSchema,
)

logger = logging.getLogger(__name__)


class VolunteerService:
    """Business logic for volunteer management."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self._repo = VolunteerRepository(session, tenant_id)
        self.tenant_id = tenant_id

    # ── Create ───────────────────────────────────────────────────────────

    async def create_volunteer(
        self,
        data: VolunteerCreateSchema,
        created_by: UUID | None = None,
    ) -> VolunteerResponse:
        """Create a new volunteer profile."""
        volunteer = await self._repo.create(
            data=data.model_dump(exclude_none=True),
            created_by=created_by,
        )
        logger.info("Volunteer profile created for member: %s", volunteer.member_id)
        return VolunteerResponse.model_validate(volunteer)

    # ── Read ─────────────────────────────────────────────────────────────

    async def get_volunteer(self, volunteer_id: UUID) -> VolunteerResponse:
        """Get a specific volunteer profile."""
        volunteer = await self._repo.get_by_id(volunteer_id)
        if not volunteer:
            raise NotFoundException("Volunteer", str(volunteer_id))
        return VolunteerResponse.model_validate(volunteer)

    async def list_volunteers(
        self,
        page: int = 1,
        per_page: int = 20,
        status: str | None = None,
        skill: str | None = None,
        availability: str | None = None,
        sort_by: str = "total_hours",
        sort_order: str = "desc",
    ) -> dict[str, Any]:
        """List volunteer profiles with pagination and filtering."""
        offset = (page - 1) * per_page

        volunteers, total = await self._repo.get_all_paginated(
            offset=offset,
            limit=per_page,
            status=status,
            skill=skill,
            availability=availability,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        total_pages = math.ceil(total / per_page) if per_page > 0 else 0
        items = [VolunteerResponse.model_validate(v) for v in volunteers]

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

    async def update_volunteer(
        self,
        volunteer_id: UUID,
        data: VolunteerUpdateSchema,
        updated_by: UUID | None = None,
    ) -> VolunteerResponse:
        """Update a volunteer profile."""
        volunteer = await self._repo.update(
            volunteer_id=volunteer_id,
            data=data.model_dump(exclude_unset=True),
            updated_by=updated_by,
        )
        if not volunteer:
            raise NotFoundException("Volunteer", str(volunteer_id))
            
        return VolunteerResponse.model_validate(volunteer)

    # ── Delete ───────────────────────────────────────────────────────────

    async def delete_volunteer(
        self, volunteer_id: UUID, deleted_by: UUID | None = None
    ) -> dict:
        """Soft-delete a volunteer profile."""
        success = await self._repo.soft_delete(volunteer_id, deleted_by)
        if not success:
            raise NotFoundException("Volunteer", str(volunteer_id))
        logger.info("Volunteer soft-deleted: %s by %s", volunteer_id, deleted_by)
        return {"message": "Volunteer deleted successfully"}

    # ── Assignments ──────────────────────────────────────────────────────

    async def assign_volunteer(
        self, 
        volunteer_id: UUID, 
        data: VolunteerAssignmentCreateSchema, 
        created_by: UUID | None = None
    ) -> VolunteerAssignmentResponse:
        """Assign a volunteer to an event."""
        # Ensure volunteer exists
        volunteer = await self._repo.get_by_id(volunteer_id)
        if not volunteer:
            raise NotFoundException("Volunteer", str(volunteer_id))

        assignment = await self._repo.assign_volunteer(
            volunteer_id=volunteer_id,
            event_id=data.event_id,
            role=data.role,
            created_by=created_by,
        )
        return VolunteerAssignmentResponse.model_validate(assignment)

    async def get_assignments(self, volunteer_id: UUID) -> list[VolunteerAssignmentResponse]:
        """Get all assignments for a volunteer."""
        assignments = await self._repo.get_assignments_for_volunteer(volunteer_id)
        return [VolunteerAssignmentResponse.model_validate(a) for a in assignments]

    async def update_assignment(
        self,
        assignment_id: UUID,
        data: VolunteerAssignmentUpdateSchema,
        updated_by: UUID | None = None
    ) -> VolunteerAssignmentResponse:
        """
        Update an assignment (e.g. check-out, log hours).
        If 'hours' or 'attended' is updated, trigger a recalculation of the volunteer's global stats.
        """
        update_data = data.model_dump(exclude_unset=True)
        assignment = await self._repo.update_assignment(
            assignment_id=assignment_id,
            data=update_data,
            updated_by=updated_by
        )
        
        if not assignment:
            raise NotFoundException("VolunteerAssignment", str(assignment_id))
            
        # If attendance or hours are updated, recalculate the volunteer stats
        if "hours" in update_data or "attended" in update_data:
            await self._repo.update_volunteer_stats(assignment.volunteer_id)
            
        return VolunteerAssignmentResponse.model_validate(assignment)
