"""
ApnaSamaj – Family API Routes

All family management endpoints scoped to the current tenant:
  • POST   /families                   – Create a family unit
  • GET    /families                   – List families
  • GET    /families/{id}              – Get family + flat member list
  • GET    /families/{id}/tree         – Get family multi-generation tree
  • PATCH  /families/{id}              – Update family
  • DELETE /families/{id}              – Delete family
  • POST   /families/{id}/members      – Link a member to family
  • DELETE /families/{id}/members/{m}  – Unlink member
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.base_schema import ApiResponse, PaginatedResponse
from apps.api.core.database import get_db
from apps.api.core.dependencies import get_current_tenant_id, get_current_user_id
from apps.api.core.permissions import Permission, RequirePermissions
from apps.api.modules.family.schemas import (
    AddFamilyMemberSchema,
    FamilyCreateSchema,
    FamilyMemberResponse,
    FamilyResponse,
    FamilyTreeResponse,
    FamilyUpdateSchema,
)
from apps.api.modules.family.service import FamilyService

router = APIRouter(prefix="/families", tags=["Families"])


# ── Create ───────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=ApiResponse[FamilyResponse],
    summary="Create Family",
    dependencies=[Depends(RequirePermissions(Permission.FAMILY_CREATE))],
)
async def create_family(
    body: FamilyCreateSchema,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[FamilyResponse]:
    service = FamilyService(db, tenant_id)
    result = await service.create_family(body, created_by=user_id)
    return ApiResponse(data=result)


# ── Read ─────────────────────────────────────────────────────────────────

@router.get(
    "",
    response_model=PaginatedResponse[FamilyResponse],
    summary="List Families",
    dependencies=[Depends(RequirePermissions(Permission.FAMILY_READ))],
)
async def list_families(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, max_length=255),
    sort_by: str = Query(default="name"),
    sort_order: str = Query(default="asc", pattern="^(asc|desc)$"),
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[FamilyResponse]:
    service = FamilyService(db, tenant_id)
    result = await service.list_families(
        page=page,
        per_page=per_page,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return PaginatedResponse(data=result["items"], meta=result["meta"])


@router.get(
    "/{family_id}",
    response_model=ApiResponse[FamilyResponse],
    summary="Get Family",
    dependencies=[Depends(RequirePermissions(Permission.FAMILY_READ))],
)
async def get_family(
    family_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[FamilyResponse]:
    service = FamilyService(db, tenant_id)
    result = await service.get_family(family_id)
    return ApiResponse(data=result)


@router.get(
    "/{family_id}/tree",
    response_model=ApiResponse[FamilyTreeResponse],
    summary="Get Family Tree",
    description="Returns the family structured as a multi-generation hierarchical tree.",
    dependencies=[Depends(RequirePermissions(Permission.FAMILY_READ))],
)
async def get_family_tree(
    family_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[FamilyTreeResponse]:
    service = FamilyService(db, tenant_id)
    result = await service.get_family_tree(family_id)
    return ApiResponse(data=result)


# ── Update ───────────────────────────────────────────────────────────────

@router.patch(
    "/{family_id}",
    response_model=ApiResponse[FamilyResponse],
    summary="Update Family",
    dependencies=[Depends(RequirePermissions(Permission.FAMILY_UPDATE))],
)
async def update_family(
    family_id: UUID,
    body: FamilyUpdateSchema,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[FamilyResponse]:
    service = FamilyService(db, tenant_id)
    result = await service.update_family(family_id, body, updated_by=user_id)
    return ApiResponse(data=result)


# ── Delete ───────────────────────────────────────────────────────────────

@router.delete(
    "/{family_id}",
    response_model=ApiResponse[dict],
    summary="Delete Family",
    dependencies=[Depends(RequirePermissions(Permission.FAMILY_DELETE))],
)
async def delete_family(
    family_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    service = FamilyService(db, tenant_id)
    result = await service.delete_family(family_id, deleted_by=user_id)
    return ApiResponse(data=result)


# ── Members (Junction) ───────────────────────────────────────────────────

@router.post(
    "/{family_id}/members",
    response_model=ApiResponse[FamilyMemberResponse],
    summary="Link Member to Family",
    dependencies=[Depends(RequirePermissions(Permission.FAMILY_UPDATE))],
)
async def add_family_member(
    family_id: UUID,
    body: AddFamilyMemberSchema,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[FamilyMemberResponse]:
    service = FamilyService(db, tenant_id)
    result = await service.add_member(
        family_id=family_id,
        data=body,
        created_by=user_id,
    )
    return ApiResponse(data=result)


@router.delete(
    "/{family_id}/members/{member_id}",
    response_model=ApiResponse[dict],
    summary="Unlink Member from Family",
    dependencies=[Depends(RequirePermissions(Permission.FAMILY_UPDATE))],
)
async def remove_family_member(
    family_id: UUID,
    member_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    service = FamilyService(db, tenant_id)
    result = await service.remove_member(family_id, member_id)
    return ApiResponse(data=result)
