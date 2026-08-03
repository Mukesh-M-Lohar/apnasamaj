"""
ApnaSamaj – Complaint Service

Business logic for managing complaints and issue state transitions.
"""

from __future__ import annotations

import logging
import math
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.exceptions import NotFoundException
from apps.api.modules.complaint.models import ComplaintStatus
from apps.api.modules.complaint.repository import ComplaintRepository
from apps.api.modules.complaint.schemas import (
    ComplaintCreateSchema,
    ComplaintResponse,
    ComplaintUpdateSchema,
)

logger = logging.getLogger(__name__)


class ComplaintService:
    """Business logic for complaint management."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self._repo = ComplaintRepository(session, tenant_id)
        self.tenant_id = tenant_id

    # ── Create ───────────────────────────────────────────────────────────

    async def create_complaint(
        self,
        data: ComplaintCreateSchema,
        reporter_id: UUID,
    ) -> ComplaintResponse:
        """Raise a new ticket/complaint."""
        payload = data.model_dump(exclude_none=True)
        payload["reporter_id"] = reporter_id

        complaint = await self._repo.create(
            data=payload,
            created_by=reporter_id,
        )
        logger.info("Complaint created by member: %s", reporter_id)
        return ComplaintResponse.model_validate(complaint)

    # ── Read ─────────────────────────────────────────────────────────────

    async def get_complaint(self, complaint_id: UUID) -> ComplaintResponse:
        """Get a specific complaint."""
        complaint = await self._repo.get_by_id(complaint_id)
        if not complaint:
            raise NotFoundException("Complaint", str(complaint_id))
        return ComplaintResponse.model_validate(complaint)

    async def list_complaints(
        self,
        page: int = 1,
        per_page: int = 20,
        status: ComplaintStatus | None = None,
        reporter_id: UUID | None = None,
        committee_id: UUID | None = None,
    ) -> dict[str, Any]:
        """List complaints with filtering and pagination."""
        offset = (page - 1) * per_page

        complaints, total = await self._repo.get_all_paginated(
            offset=offset,
            limit=per_page,
            status=status,
            reporter_id=reporter_id,
            committee_id=committee_id,
        )

        total_pages = math.ceil(total / per_page) if per_page > 0 else 0
        items = [ComplaintResponse.model_validate(c) for c in complaints]

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

    async def update_complaint(
        self,
        complaint_id: UUID,
        data: ComplaintUpdateSchema,
        updated_by: UUID | None = None,
    ) -> ComplaintResponse:
        """Update complaint details (status transitions, resolution notes)."""
        complaint = await self._repo.update(
            complaint_id=complaint_id,
            data=data.model_dump(exclude_unset=True),
            updated_by=updated_by,
        )
        if not complaint:
            raise NotFoundException("Complaint", str(complaint_id))

        return ComplaintResponse.model_validate(complaint)

    # ── Delete ───────────────────────────────────────────────────────────

    async def delete_complaint(self, complaint_id: UUID, deleted_by: UUID | None = None) -> dict:
        """Soft-delete a complaint."""
        success = await self._repo.soft_delete(complaint_id, deleted_by)
        if not success:
            raise NotFoundException("Complaint", str(complaint_id))
        logger.info("Complaint soft-deleted: %s by %s", complaint_id, deleted_by)
        return {"message": "Complaint deleted successfully"}
