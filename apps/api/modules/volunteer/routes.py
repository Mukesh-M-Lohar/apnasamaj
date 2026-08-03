"""
ApnaSamaj – Volunteer API Routes

All volunteer endpoints scoped to the current tenant:
  • POST   /volunteers                   – Create volunteer
  • GET    /volunteers                   – List volunteers
  • GET    /volunteers/{id}              – Get volunteer details
  • PATCH  /volunteers/{id}              – Update volunteer
  • DELETE /volunteers/{id}              – Delete volunteer
  • POST   /volunteers/{id}/assignments  – Assign to event
  • GET    /volunteers/{id}/assignments  – View history
  • PATCH  /volunteers/assignments/{id}  – Log hours & check-out
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.base_schema import ApiResponse, PaginatedResponse
from apps.api.core.database import get_db
from apps.api.core.dependencies import get_current_tenant_id, get_current_user_id
from apps.api.core.permissions import Permission, RequirePermissions
from apps.api.modules.volunteer.schemas import (
    VolunteerAssignmentCreateSchema,
    VolunteerAssignmentResponse,
    VolunteerAssignmentUpdateSchema,
    VolunteerCreateSchema,
    VolunteerResponse,
    VolunteerUpdateSchema,
)
from apps.api.modules.volunteer.service import VolunteerService

router = APIRouter(prefix="/volunteers", tags=["Volunteers"])


# ── Profiles ─────────────────────────────────────────────────────────────


@router.post(
    "",
    response_model=ApiResponse[VolunteerResponse],
    summary="Create Volunteer",
    dependencies=[Depends(RequirePermissions(Permission.VOLUNTEER_CREATE))],
)
async def create_volunteer(
    body: VolunteerCreateSchema,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[VolunteerResponse]:
    service = VolunteerService(db, tenant_id)
    result = await service.create_volunteer(body, created_by=user_id)
    return ApiResponse(data=result)


@router.get(
    "",
    response_model=PaginatedResponse[VolunteerResponse],
    summary="List Volunteers",
    dependencies=[Depends(RequirePermissions(Permission.VOLUNTEER_READ))],
)
async def list_volunteers(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    skill: str | None = Query(default=None),
    availability: str | None = Query(default=None),
    sort_by: str = Query(default="total_hours"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[VolunteerResponse]:
    service = VolunteerService(db, tenant_id)
    result = await service.list_volunteers(
        page=page,
        per_page=per_page,
        status=status,
        skill=skill,
        availability=availability,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return PaginatedResponse(data=result["items"], meta=result["meta"])


@router.get(
    "/{volunteer_id}",
    response_model=ApiResponse[VolunteerResponse],
    summary="Get Volunteer",
    dependencies=[Depends(RequirePermissions(Permission.VOLUNTEER_READ))],
)
async def get_volunteer(
    volunteer_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[VolunteerResponse]:
    service = VolunteerService(db, tenant_id)
    result = await service.get_volunteer(volunteer_id)
    return ApiResponse(data=result)


@router.patch(
    "/{volunteer_id}",
    response_model=ApiResponse[VolunteerResponse],
    summary="Update Volunteer",
    dependencies=[Depends(RequirePermissions(Permission.VOLUNTEER_UPDATE))],
)
async def update_volunteer(
    volunteer_id: UUID,
    body: VolunteerUpdateSchema,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[VolunteerResponse]:
    service = VolunteerService(db, tenant_id)
    result = await service.update_volunteer(volunteer_id, body, updated_by=user_id)
    return ApiResponse(data=result)


@router.delete(
    "/{volunteer_id}",
    response_model=ApiResponse[dict],
    summary="Delete Volunteer",
    dependencies=[Depends(RequirePermissions(Permission.VOLUNTEER_DELETE))],
)
async def delete_volunteer(
    volunteer_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    service = VolunteerService(db, tenant_id)
    result = await service.delete_volunteer(volunteer_id, deleted_by=user_id)
    return ApiResponse(data=result)


# ── Assignments ──────────────────────────────────────────────────────────


@router.get(
    "/{volunteer_id}/assignments",
    response_model=ApiResponse[list[VolunteerAssignmentResponse]],
    summary="List Assignments",
    dependencies=[Depends(RequirePermissions(Permission.VOLUNTEER_READ))],
)
async def get_assignments(
    volunteer_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[list[VolunteerAssignmentResponse]]:
    service = VolunteerService(db, tenant_id)
    result = await service.get_assignments(volunteer_id)
    return ApiResponse(data=result)


@router.post(
    "/{volunteer_id}/assignments",
    response_model=ApiResponse[VolunteerAssignmentResponse],
    summary="Assign Volunteer",
    dependencies=[Depends(RequirePermissions(Permission.VOLUNTEER_UPDATE))],
)
async def assign_volunteer(
    volunteer_id: UUID,
    body: VolunteerAssignmentCreateSchema,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[VolunteerAssignmentResponse]:
    service = VolunteerService(db, tenant_id)
    result = await service.assign_volunteer(volunteer_id, body, created_by=user_id)
    return ApiResponse(data=result)


@router.patch(
    "/assignments/{assignment_id}",
    response_model=ApiResponse[VolunteerAssignmentResponse],
    summary="Update Assignment / Log Hours",
    description="Update a volunteer assignment. If 'hours' or 'attended' are modified, global volunteer stats are automatically recalculated.",
    dependencies=[Depends(RequirePermissions(Permission.VOLUNTEER_UPDATE))],
)
async def update_assignment(
    assignment_id: UUID,
    body: VolunteerAssignmentUpdateSchema,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[VolunteerAssignmentResponse]:
    service = VolunteerService(db, tenant_id)
    result = await service.update_assignment(assignment_id, body, updated_by=user_id)
    return ApiResponse(data=result)
