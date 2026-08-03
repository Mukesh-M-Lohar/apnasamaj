"""
ApnaSamaj – Complaint API Routes

All complaint endpoints scoped to the current tenant:
  • POST   /complaints      – Raise a new ticket
  • GET    /complaints      – List tickets (filterable by status, reporter, committee)
  • GET    /complaints/{id} – Get ticket details
  • PATCH  /complaints/{id} – Update ticket (status, assignment)
  • DELETE /complaints/{id} – Delete ticket
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.base_schema import ApiResponse, PaginatedResponse
from apps.api.core.database import get_db
from apps.api.core.dependencies import get_current_tenant_id, get_current_user_id
from apps.api.core.permissions import Permission, RequirePermissions
from apps.api.modules.complaint.models import ComplaintStatus
from apps.api.modules.complaint.schemas import (
    ComplaintCreateSchema,
    ComplaintResponse,
    ComplaintUpdateSchema,
)
from apps.api.modules.complaint.service import ComplaintService

router = APIRouter(prefix="/complaints", tags=["Complaints"])


@router.post(
    "",
    response_model=ApiResponse[ComplaintResponse],
    summary="Raise Complaint",
    description="Submit a new issue or suggestion.",
    # Depending on config, members could raise it without admin permission,
    # but we'll use a generic permission or rely on user_id.
    # Here we assume any authenticated user can raise a complaint if they have basic access.
)
async def create_complaint(
    body: ComplaintCreateSchema,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ComplaintResponse]:
    service = ComplaintService(db, tenant_id)
    # Using user_id as the reporter_id for now. In a real app,
    # we would look up their Member ID via user_id.
    result = await service.create_complaint(body, reporter_id=user_id)
    return ApiResponse(data=result)


@router.get(
    "",
    response_model=PaginatedResponse[ComplaintResponse],
    summary="List Complaints",
)
async def list_complaints(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    status: ComplaintStatus | None = Query(default=None),
    reporter_id: UUID | None = Query(default=None),
    committee_id: UUID | None = Query(default=None),
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[ComplaintResponse]:
    service = ComplaintService(db, tenant_id)
    result = await service.list_complaints(
        page=page,
        per_page=per_page,
        status=status,
        reporter_id=reporter_id,
        committee_id=committee_id,
    )
    return PaginatedResponse(data=result["items"], meta=result["meta"])


@router.get(
    "/{complaint_id}",
    response_model=ApiResponse[ComplaintResponse],
    summary="Get Complaint",
)
async def get_complaint(
    complaint_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ComplaintResponse]:
    service = ComplaintService(db, tenant_id)
    result = await service.get_complaint(complaint_id)
    return ApiResponse(data=result)


@router.patch(
    "/{complaint_id}",
    response_model=ApiResponse[ComplaintResponse],
    summary="Update Complaint",
    description="Update status, assign committee, or add resolution notes.",
    dependencies=[Depends(RequirePermissions(Permission.COMMUNITY_UPDATE))],  # Requires some elevated access
)
async def update_complaint(
    complaint_id: UUID,
    body: ComplaintUpdateSchema,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ComplaintResponse]:
    service = ComplaintService(db, tenant_id)
    result = await service.update_complaint(complaint_id, body, updated_by=user_id)
    return ApiResponse(data=result)


@router.delete(
    "/{complaint_id}",
    response_model=ApiResponse[dict],
    summary="Delete Complaint",
    dependencies=[Depends(RequirePermissions(Permission.COMMUNITY_DELETE))],
)
async def delete_complaint(
    complaint_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    service = ComplaintService(db, tenant_id)
    result = await service.delete_complaint(complaint_id, deleted_by=user_id)
    return ApiResponse(data=result)
