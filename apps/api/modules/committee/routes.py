"""
ApnaSamaj – Committee API Routes

All committee management endpoints scoped to the current tenant:
  • POST   /committees                   – Create a committee
  • GET    /committees                   – List committees
  • GET    /committees/{id}              – Get committee with members
  • PATCH  /committees/{id}              – Update committee
  • DELETE /committees/{id}              – Delete committee
  • POST   /committees/{id}/members      – Link a member
  • DELETE /committees/{id}/members/{m}  – Unlink member
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.base_schema import ApiResponse, PaginatedResponse
from apps.api.core.database import get_db
from apps.api.core.dependencies import get_current_tenant_id, get_current_user_id
from apps.api.core.permissions import Permission, RequirePermissions
from apps.api.modules.committee.schemas import (
    AddCommitteeMemberSchema,
    CommitteeCreateSchema,
    CommitteeMemberResponse,
    CommitteeResponse,
    CommitteeUpdateSchema,
)
from apps.api.modules.committee.service import CommitteeService

router = APIRouter(prefix="/committees", tags=["Committees"])


# ── Create ───────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=ApiResponse[CommitteeResponse],
    summary="Create Committee",
    dependencies=[Depends(RequirePermissions(Permission.COMMITTEE_CREATE))],
)
async def create_committee(
    body: CommitteeCreateSchema,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[CommitteeResponse]:
    service = CommitteeService(db, tenant_id)
    result = await service.create_committee(body, created_by=user_id)
    return ApiResponse(data=result)


# ── Read ─────────────────────────────────────────────────────────────────

@router.get(
    "",
    response_model=PaginatedResponse[CommitteeResponse],
    summary="List Committees",
    dependencies=[Depends(RequirePermissions(Permission.COMMITTEE_READ))],
)
async def list_committees(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, max_length=255),
    status: str | None = Query(default=None),
    sort_by: str = Query(default="name"),
    sort_order: str = Query(default="asc", pattern="^(asc|desc)$"),
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[CommitteeResponse]:
    service = CommitteeService(db, tenant_id)
    result = await service.list_committees(
        page=page,
        per_page=per_page,
        search=search,
        status=status,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return PaginatedResponse(data=result["items"], meta=result["meta"])


@router.get(
    "/{committee_id}",
    response_model=ApiResponse[CommitteeResponse],
    summary="Get Committee",
    dependencies=[Depends(RequirePermissions(Permission.COMMITTEE_READ))],
)
async def get_committee(
    committee_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[CommitteeResponse]:
    service = CommitteeService(db, tenant_id)
    result = await service.get_committee(committee_id)
    return ApiResponse(data=result)


# ── Update ───────────────────────────────────────────────────────────────

@router.patch(
    "/{committee_id}",
    response_model=ApiResponse[CommitteeResponse],
    summary="Update Committee",
    dependencies=[Depends(RequirePermissions(Permission.COMMITTEE_UPDATE))],
)
async def update_committee(
    committee_id: UUID,
    body: CommitteeUpdateSchema,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[CommitteeResponse]:
    service = CommitteeService(db, tenant_id)
    result = await service.update_committee(committee_id, body, updated_by=user_id)
    return ApiResponse(data=result)


# ── Delete ───────────────────────────────────────────────────────────────

@router.delete(
    "/{committee_id}",
    response_model=ApiResponse[dict],
    summary="Delete Committee",
    dependencies=[Depends(RequirePermissions(Permission.COMMITTEE_DELETE))],
)
async def delete_committee(
    committee_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    service = CommitteeService(db, tenant_id)
    result = await service.delete_committee(committee_id, deleted_by=user_id)
    return ApiResponse(data=result)


# ── Members (Junction) ───────────────────────────────────────────────────

@router.post(
    "/{committee_id}/members",
    response_model=ApiResponse[CommitteeMemberResponse],
    summary="Assign Member to Committee",
    dependencies=[Depends(RequirePermissions(Permission.COMMITTEE_UPDATE))],
)
async def add_committee_member(
    committee_id: UUID,
    body: AddCommitteeMemberSchema,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[CommitteeMemberResponse]:
    service = CommitteeService(db, tenant_id)
    result = await service.add_member(
        committee_id=committee_id,
        data=body,
        created_by=user_id,
    )
    return ApiResponse(data=result)


@router.delete(
    "/{committee_id}/members/{member_id}",
    response_model=ApiResponse[dict],
    summary="Remove Member from Committee",
    dependencies=[Depends(RequirePermissions(Permission.COMMITTEE_UPDATE))],
)
async def remove_committee_member(
    committee_id: UUID,
    member_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    service = CommitteeService(db, tenant_id)
    result = await service.remove_member(committee_id, member_id)
    return ApiResponse(data=result)
