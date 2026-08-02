"""
ApnaSamaj – Donation Service

Business logic for financial donations including receipt generation.
"""

from __future__ import annotations

import logging
import math
from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.exceptions import NotFoundException
from apps.api.modules.donation.repository import DonationRepository
from apps.api.modules.donation.schemas import (
    DonationCreateSchema,
    DonationResponse,
    DonationSummaryResponse,
    DonationUpdateSchema,
)

logger = logging.getLogger(__name__)


class DonationService:
    """Business logic for donation management."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self._repo = DonationRepository(session, tenant_id)
        self.tenant_id = tenant_id

    async def _generate_receipt_number(self) -> str:
        """
        Generate a unique receipt number: RCPT-{YEAR}-{SEQ}
        Example: RCPT-2024-0001
        """
        current_year = date.today().year
        prefix = f"RCPT-{current_year}-"
        
        last_receipt = await self._repo.get_last_receipt_number(prefix)
        if last_receipt:
            # Extract the sequence part and increment
            try:
                seq = int(last_receipt.split("-")[-1])
                next_seq = seq + 1
            except ValueError:
                next_seq = 1
        else:
            next_seq = 1
            
        return f"{prefix}{next_seq:04d}"

    # ── Create ───────────────────────────────────────────────────────────

    async def create_donation(
        self,
        data: DonationCreateSchema,
        created_by: UUID | None = None,
    ) -> DonationResponse:
        """Create a new donation and auto-generate receipt."""
        
        create_data = data.model_dump(exclude_none=True)
        
        # Auto-generate receipt number
        create_data["receipt_number"] = await self._generate_receipt_number()
        
        donation = await self._repo.create(
            data=create_data,
            created_by=created_by,
        )
        logger.info("Donation created: %s, Amount: %s", donation.receipt_number, donation.amount)
        return DonationResponse.model_validate(donation)

    # ── Read ─────────────────────────────────────────────────────────────

    async def get_donation(self, donation_id: UUID) -> DonationResponse:
        """Get a specific donation."""
        donation = await self._repo.get_by_id(donation_id)
        if not donation:
            raise NotFoundException("Donation", str(donation_id))
        return DonationResponse.model_validate(donation)

    async def list_donations(
        self,
        page: int = 1,
        per_page: int = 20,
        purpose: str | None = None,
        payment_mode: str | None = None,
        member_id: UUID | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        sort_by: str = "donation_date",
        sort_order: str = "desc",
    ) -> dict[str, Any]:
        """List donations with filtering and pagination."""
        offset = (page - 1) * per_page

        donations, total = await self._repo.get_all_paginated(
            offset=offset,
            limit=per_page,
            purpose=purpose,
            payment_mode=payment_mode,
            member_id=member_id,
            start_date=start_date,
            end_date=end_date,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        total_pages = math.ceil(total / per_page) if per_page > 0 else 0

        items = [DonationResponse.model_validate(d) for d in donations]

        return {
            "items": items,
            "meta": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            },
        }

    async def get_summary(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> DonationSummaryResponse:
        """Get a financial rollup for the dashboard."""
        summary = await self._repo.get_summary(start_date, end_date)
        return DonationSummaryResponse(
            total_donations=summary["total_amount"],
            total_count=summary["total_count"],
            by_purpose=summary["by_purpose"],
            by_payment_mode=summary["by_payment_mode"],
        )

    # ── Update ───────────────────────────────────────────────────────────

    async def update_donation(
        self,
        donation_id: UUID,
        data: DonationUpdateSchema,
        updated_by: UUID | None = None,
    ) -> DonationResponse:
        """Update a donation record."""
        donation = await self._repo.update(
            donation_id=donation_id,
            data=data.model_dump(exclude_unset=True),
            updated_by=updated_by,
        )
        if not donation:
            raise NotFoundException("Donation", str(donation_id))
            
        return DonationResponse.model_validate(donation)

    # ── Delete ───────────────────────────────────────────────────────────

    async def delete_donation(
        self, donation_id: UUID, deleted_by: UUID | None = None
    ) -> dict:
        """Soft-delete a donation record."""
        success = await self._repo.soft_delete(donation_id, deleted_by)
        if not success:
            raise NotFoundException("Donation", str(donation_id))
        logger.info("Donation soft-deleted: %s by %s", donation_id, deleted_by)
        return {"message": "Donation deleted successfully"}
