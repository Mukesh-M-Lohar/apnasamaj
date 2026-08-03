"""
ApnaSamaj – Donation Repository

Database operations for tracking financial donations.
"""

from __future__ import annotations

from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy import Select, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.modules.donation.models import Donation


class DonationRepository:
    """Handles donation DB operations scoped to a tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self._session = session
        self.tenant_id = tenant_id

    def _base_query(self) -> Select:
        return select(Donation).where(
            Donation.tenant_id == self.tenant_id,
            Donation.is_deleted == False,  # noqa: E712
        )

    # ── Create ───────────────────────────────────────────────────────────

    async def create(self, data: dict[str, Any], created_by: UUID | None = None) -> Donation:
        donation = Donation(
            tenant_id=self.tenant_id,
            created_by=created_by,
            updated_by=created_by,
            **data,
        )
        self._session.add(donation)
        await self._session.flush()
        await self._session.refresh(donation)
        return donation

    # ── Read ─────────────────────────────────────────────────────────────

    async def get_by_id(self, donation_id: UUID) -> Donation | None:
        stmt = self._base_query().where(Donation.id == donation_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_last_receipt_number(self, prefix: str) -> str | None:
        """Fetch the highest receipt number starting with the given prefix."""
        stmt = (
            select(Donation.receipt_number)
            .where(Donation.tenant_id == self.tenant_id, Donation.receipt_number.like(f"{prefix}%"))
            .order_by(Donation.receipt_number.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_paginated(
        self,
        offset: int = 0,
        limit: int = 20,
        purpose: str | None = None,
        payment_mode: str | None = None,
        member_id: UUID | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        sort_by: str = "donation_date",
        sort_order: str = "desc",
    ) -> tuple[list[Donation], int]:
        stmt = self._base_query()
        count_stmt = (
            select(func.count())
            .select_from(Donation)
            .where(
                Donation.tenant_id == self.tenant_id,
                Donation.is_deleted == False,  # noqa: E712
            )
        )

        if purpose:
            stmt = stmt.where(Donation.purpose == purpose)
            count_stmt = count_stmt.where(Donation.purpose == purpose)

        if payment_mode:
            stmt = stmt.where(Donation.payment_mode == payment_mode)
            count_stmt = count_stmt.where(Donation.payment_mode == payment_mode)

        if member_id:
            stmt = stmt.where(Donation.member_id == member_id)
            count_stmt = count_stmt.where(Donation.member_id == member_id)

        if start_date:
            stmt = stmt.where(Donation.donation_date >= start_date)
            count_stmt = count_stmt.where(Donation.donation_date >= start_date)

        if end_date:
            stmt = stmt.where(Donation.donation_date <= end_date)
            count_stmt = count_stmt.where(Donation.donation_date <= end_date)

        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        sort_column = getattr(Donation, sort_by, Donation.donation_date)
        stmt = stmt.order_by(sort_column.desc() if sort_order == "desc" else sort_column.asc())
        stmt = stmt.offset(offset).limit(limit)

        result = await self._session.execute(stmt)
        donations = list(result.scalars().all())

        return donations, total

    # ── Rollups / Summary ────────────────────────────────────────────────

    async def get_summary(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> dict[str, Any]:
        """Generate financial rollups grouped by purpose and payment_mode."""
        base_filter = [
            Donation.tenant_id == self.tenant_id,
            Donation.is_deleted == False,  # noqa: E712
            Donation.status == "completed",
        ]

        if start_date:
            base_filter.append(Donation.donation_date >= start_date)
        if end_date:
            base_filter.append(Donation.donation_date <= end_date)

        # 1. Total sum and count
        total_stmt = select(
            func.sum(Donation.amount).label("total_amount"), func.count(Donation.id).label("total_count")
        ).where(*base_filter)
        total_res = await self._session.execute(total_stmt)
        total_row = total_res.first()

        # 2. Group by purpose
        purpose_stmt = (
            select(
                Donation.purpose,
                func.sum(Donation.amount).label("total_amount"),
                func.count(Donation.id).label("count"),
            )
            .where(*base_filter)
            .group_by(Donation.purpose)
        )
        purpose_res = await self._session.execute(purpose_stmt)

        # 3. Group by payment mode
        mode_stmt = (
            select(
                Donation.payment_mode,
                func.sum(Donation.amount).label("total_amount"),
                func.count(Donation.id).label("count"),
            )
            .where(*base_filter)
            .group_by(Donation.payment_mode)
        )
        mode_res = await self._session.execute(mode_stmt)

        return {
            "total_amount": total_row.total_amount or 0,
            "total_count": total_row.total_count or 0,
            "by_purpose": [
                {"group_key": row.purpose, "total_amount": row.total_amount, "count": row.count} for row in purpose_res
            ],
            "by_payment_mode": [
                {"group_key": row.payment_mode, "total_amount": row.total_amount, "count": row.count}
                for row in mode_res
            ],
        }

    # ── Update ───────────────────────────────────────────────────────────

    async def update(self, donation_id: UUID, data: dict[str, Any], updated_by: UUID | None = None) -> Donation | None:
        donation = await self.get_by_id(donation_id)
        if not donation:
            return None

        for key, value in data.items():
            if value is not None and hasattr(donation, key):
                setattr(donation, key, value)

        if updated_by:
            donation.updated_by = updated_by

        await self._session.flush()
        await self._session.refresh(donation)
        return donation

    # ── Delete ───────────────────────────────────────────────────────────

    async def soft_delete(self, donation_id: UUID, deleted_by: UUID | None = None) -> bool:
        stmt = (
            update(Donation)
            .where(
                Donation.id == donation_id,
                Donation.tenant_id == self.tenant_id,
                Donation.is_deleted == False,  # noqa: E712
            )
            .values(is_deleted=True, updated_by=deleted_by)
        )
        from datetime import UTC, datetime

        stmt = stmt.values(deleted_at=datetime.now(UTC))

        result = await self._session.execute(stmt)
        return result.rowcount > 0
