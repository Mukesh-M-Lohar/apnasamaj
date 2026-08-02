"""
ApnaSamaj – Donation API Routes

All donation endpoints scoped to the current tenant:
  • GET    /donations/summary    – Financial rollups
  • POST   /donations            – Create donation
  • GET    /donations            – List donations
  • GET    /donations/{id}       – Get donation
  • PATCH  /donations/{id}       – Update donation
  • DELETE /donations/{id}       – Delete donation
"""

from __future__ import annotations

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.base_schema import ApiResponse, PaginatedResponse
from apps.api.core.database import get_db
from apps.api.core.dependencies import get_current_tenant_id, get_current_user_id
from apps.api.core.permissions import Permission, RequirePermissions
from apps.api.modules.donation.schemas import (
    DonationCreateSchema,
    DonationResponse,
    DonationSummaryResponse,
    DonationUpdateSchema,
)
from apps.api.modules.donation.service import DonationService

router = APIRouter(prefix="/donations", tags=["Donations"])


# ── Rollups / Summary ────────────────────────────────────────────────────

@router.get(
    "/summary",
    response_model=ApiResponse[DonationSummaryResponse],
    summary="Donation Summary (Dashboard)",
    dependencies=[Depends(RequirePermissions(Permission.DONATION_READ))],
)
async def get_donation_summary(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[DonationSummaryResponse]:
    service = DonationService(db, tenant_id)
    result = await service.get_summary(start_date, end_date)
    return ApiResponse(data=result)


# ── Create ───────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=ApiResponse[DonationResponse],
    summary="Create Donation",
    dependencies=[Depends(RequirePermissions(Permission.DONATION_CREATE))],
)
async def create_donation(
    body: DonationCreateSchema,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[DonationResponse]:
    service = DonationService(db, tenant_id)
    result = await service.create_donation(body, created_by=user_id)
    return ApiResponse(data=result)


# ── Read ─────────────────────────────────────────────────────────────────

@router.get(
    "",
    response_model=PaginatedResponse[DonationResponse],
    summary="List Donations",
    dependencies=[Depends(RequirePermissions(Permission.DONATION_READ))],
)
async def list_donations(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    purpose: str | None = Query(default=None),
    payment_mode: str | None = Query(default=None),
    member_id: UUID | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    sort_by: str = Query(default="donation_date"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[DonationResponse]:
    service = DonationService(db, tenant_id)
    result = await service.list_donations(
        page=page,
        per_page=per_page,
        purpose=purpose,
        payment_mode=payment_mode,
        member_id=member_id,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return PaginatedResponse(data=result["items"], meta=result["meta"])


@router.get(
    "/{donation_id}",
    response_model=ApiResponse[DonationResponse],
    summary="Get Donation",
    dependencies=[Depends(RequirePermissions(Permission.DONATION_READ))],
)
async def get_donation(
    donation_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[DonationResponse]:
    service = DonationService(db, tenant_id)
    result = await service.get_donation(donation_id)
    return ApiResponse(data=result)


# ── Update ───────────────────────────────────────────────────────────────

@router.patch(
    "/{donation_id}",
    response_model=ApiResponse[DonationResponse],
    summary="Update Donation",
    dependencies=[Depends(RequirePermissions(Permission.DONATION_UPDATE))],
)
async def update_donation(
    donation_id: UUID,
    body: DonationUpdateSchema,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[DonationResponse]:
    service = DonationService(db, tenant_id)
    result = await service.update_donation(donation_id, body, updated_by=user_id)
    return ApiResponse(data=result)


# ── Delete ───────────────────────────────────────────────────────────────

@router.delete(
    "/{donation_id}",
    response_model=ApiResponse[dict],
    summary="Delete Donation",
    dependencies=[Depends(RequirePermissions(Permission.DONATION_DELETE))],
)
async def delete_donation(
    donation_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    service = DonationService(db, tenant_id)
    result = await service.delete_donation(donation_id, deleted_by=user_id)
    return ApiResponse(data=result)
