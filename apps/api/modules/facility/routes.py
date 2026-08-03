"""
ApnaSamaj – Facility API Routes

Endpoints for managing assets and their bookings:
  • POST   /facilities
  • GET    /facilities
  • GET    /facilities/{id}
  • PATCH  /facilities/{id}
  • DELETE /facilities/{id}
  • POST   /facilities/{id}/book
  • GET    /facilities/{id}/bookings
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.base_schema import ApiResponse, PaginatedResponse
from apps.api.core.database import get_db
from apps.api.core.dependencies import get_current_tenant_id, get_current_user_id
from apps.api.core.permissions import Permission, RequirePermissions
from apps.api.modules.facility.schemas import (
    FacilityBookingCreateSchema,
    FacilityBookingResponse,
    FacilityCreateSchema,
    FacilityResponse,
    FacilityUpdateSchema,
)
from apps.api.modules.facility.service import FacilityService

router = APIRouter(prefix="/facilities", tags=["Facilities"])


# ── Facilities ───────────────────────────────────────────────────────


@router.post(
    "",
    response_model=ApiResponse[FacilityResponse],
    summary="Create Facility",
    dependencies=[Depends(RequirePermissions(Permission.COMMUNITY_CREATE))],
)
async def create_facility(
    body: FacilityCreateSchema,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[FacilityResponse]:
    service = FacilityService(db, tenant_id)
    result = await service.create_facility(body, created_by=user_id)
    return ApiResponse(data=result)


@router.get(
    "",
    response_model=PaginatedResponse[FacilityResponse],
    summary="List Facilities",
)
async def list_facilities(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[FacilityResponse]:
    service = FacilityService(db, tenant_id)
    result = await service.list_facilities(page=page, per_page=per_page)
    return PaginatedResponse(data=result["items"], meta=result["meta"])


@router.get(
    "/{facility_id}",
    response_model=ApiResponse[FacilityResponse],
    summary="Get Facility",
)
async def get_facility(
    facility_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[FacilityResponse]:
    service = FacilityService(db, tenant_id)
    result = await service.get_facility(facility_id)
    return ApiResponse(data=result)


@router.patch(
    "/{facility_id}",
    response_model=ApiResponse[FacilityResponse],
    summary="Update Facility",
    dependencies=[Depends(RequirePermissions(Permission.COMMUNITY_UPDATE))],
)
async def update_facility(
    facility_id: UUID,
    body: FacilityUpdateSchema,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[FacilityResponse]:
    service = FacilityService(db, tenant_id)
    result = await service.update_facility(facility_id, body, updated_by=user_id)
    return ApiResponse(data=result)


@router.delete(
    "/{facility_id}",
    response_model=ApiResponse[dict],
    summary="Delete Facility",
    dependencies=[Depends(RequirePermissions(Permission.COMMUNITY_DELETE))],
)
async def delete_facility(
    facility_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    service = FacilityService(db, tenant_id)
    result = await service.delete_facility(facility_id, deleted_by=user_id)
    return ApiResponse(data=result)


# ── Bookings ─────────────────────────────────────────────────────────


@router.post(
    "/{facility_id}/book",
    response_model=ApiResponse[FacilityBookingResponse],
    summary="Book Facility",
)
async def book_facility(
    facility_id: UUID,
    body: FacilityBookingCreateSchema,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[FacilityBookingResponse]:
    service = FacilityService(db, tenant_id)
    result = await service.book_facility(facility_id, body, booked_by=user_id)
    return ApiResponse(data=result)


@router.get(
    "/{facility_id}/bookings",
    response_model=ApiResponse[list[FacilityBookingResponse]],
    summary="List Bookings for Facility",
)
async def get_facility_bookings(
    facility_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[list[FacilityBookingResponse]]:
    service = FacilityService(db, tenant_id)
    result = await service.get_facility_bookings(facility_id)
    return ApiResponse(data=result)
