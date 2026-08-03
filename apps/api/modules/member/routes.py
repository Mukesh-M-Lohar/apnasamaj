from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.base_schema import ApiResponse, PaginatedResponse
from apps.api.core.database import get_db
from apps.api.core.dependencies import get_current_tenant_id, get_current_user_id
from apps.api.core.permissions import Permission, RequirePermissions
from apps.api.modules.member.schemas import (
    MemberCreateSchema,
    MemberListResponse,
    MemberResponse,
    MemberUpdateSchema,
)
from apps.api.modules.member.service import MemberService

router = APIRouter(prefix="/members", tags=["Members"])


@router.post(
    "",
    response_model=ApiResponse[MemberResponse],
    summary="Create Member",
    description="Create a new member profile.",
    dependencies=[Depends(RequirePermissions(Permission.MEMBER_CREATE))],
)
async def create_member(
    body: MemberCreateSchema,
    user_id: UUID = Depends(get_current_user_id),
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[MemberResponse]:
    service = MemberService(db, tenant_id)
    result = await service.create_member(body, created_by=user_id)
    return ApiResponse(data=result)


@router.get(
    "",
    response_model=PaginatedResponse[MemberListResponse],
    summary="List Members",
    description="Get a paginated list of members with optional filtering.",
    dependencies=[Depends(RequirePermissions(Permission.MEMBER_READ))],
)
async def list_members(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None),
    status: str | None = Query(default=None),
    blood_group: str | None = Query(default=None),
    city: str | None = Query(default=None),
    gender: str | None = Query(default=None),
    sort_by: str = Query(default="first_name"),
    sort_order: str = Query(default="asc"),
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[MemberListResponse]:
    service = MemberService(db, tenant_id)
    result = await service.list_members(
        page=page,
        per_page=per_page,
        search=search,
        status=status,
        blood_group=blood_group,
        city=city,
        gender=gender,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return PaginatedResponse(**result)


@router.get(
    "/{member_id}",
    response_model=ApiResponse[MemberResponse],
    summary="Get Member",
    description="Get details of a specific member.",
    dependencies=[Depends(RequirePermissions(Permission.MEMBER_READ))],
)
async def get_member(
    member_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[MemberResponse]:
    service = MemberService(db, tenant_id)
    result = await service.get_member(member_id)
    return ApiResponse(data=result)


@router.patch(
    "/{member_id}",
    response_model=ApiResponse[MemberResponse],
    summary="Update Member",
    description="Partially update a member profile.",
    dependencies=[Depends(RequirePermissions(Permission.MEMBER_UPDATE))],
)
async def update_member(
    member_id: UUID,
    body: MemberUpdateSchema,
    user_id: UUID = Depends(get_current_user_id),
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[MemberResponse]:
    service = MemberService(db, tenant_id)
    result = await service.update_member(member_id, body, updated_by=user_id)
    return ApiResponse(data=result)


@router.delete(
    "/{member_id}",
    response_model=ApiResponse[dict],
    summary="Delete Member",
    description="Soft delete a member.",
    dependencies=[Depends(RequirePermissions(Permission.MEMBER_DELETE))],
)
async def delete_member(
    member_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    service = MemberService(db, tenant_id)
    result = await service.delete_member(member_id, deleted_by=user_id)
    return ApiResponse(data=result)
