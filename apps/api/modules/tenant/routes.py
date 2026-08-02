"""
ApnaSamaj – Community (Tenant) API Routes

All community management endpoints:
  • POST   /communities                  – Create a community
  • POST   /communities/onboard          – Onboard (create + assign admin)
  • GET    /communities                  – List all communities
  • GET    /communities/my               – List current user's communities
  • GET    /communities/{id}             – Get community details
  • GET    /communities/slug/{slug}      – Get community by slug (public)
  • PATCH  /communities/{id}             – Update community
  • PUT    /communities/{id}/settings    – Update settings
  • POST   /communities/{id}/activate    – Activate community
  • POST   /communities/{id}/deactivate  – Deactivate community
  • DELETE /communities/{id}             – Soft-delete community
  • GET    /communities/{id}/stats       – Dashboard stats
  • POST   /communities/{id}/invite      – Invite a member
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.base_schema import ApiResponse, PaginatedResponse
from apps.api.core.database import get_db
from apps.api.core.dependencies import (
    get_current_tenant_id,
    get_current_user,
    get_current_user_id,
    get_optional_user,
)
from apps.api.core.permissions import Permission, RequirePermissions
from apps.api.modules.tenant.schemas import (
    CommunityCreateSchema,
    CommunityListResponse,
    CommunityOnboardResponse,
    CommunityOnboardSchema,
    CommunityResponse,
    CommunitySettingsSchema,
    CommunityStatsResponse,
    CommunityUpdateSchema,
    InviteMemberSchema,
)
from apps.api.modules.tenant.service import CommunityService

router = APIRouter(prefix="/communities", tags=["Communities"])


# ── Create ───────────────────────────────────────────────────────────────


@router.post(
    "",
    response_model=ApiResponse[CommunityResponse],
    summary="Create Community",
    description="Create a new community / organization. Requires super admin.",
    dependencies=[Depends(RequirePermissions(Permission.COMMUNITY_CREATE))],
)
async def create_community(
    body: CommunityCreateSchema,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[CommunityResponse]:
    service = CommunityService(db)
    result = await service.create_community(body, created_by=user_id)
    return ApiResponse(data=result)


@router.post(
    "/onboard",
    response_model=ApiResponse[CommunityOnboardResponse],
    summary="Onboard Community",
    description="Create a community and become its admin. For self-service registration.",
)
async def onboard_community(
    body: CommunityOnboardSchema,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[CommunityOnboardResponse]:
    service = CommunityService(db)
    result = await service.onboard_community(body, user_id=user_id)
    return ApiResponse(data=result)


# ── Read ─────────────────────────────────────────────────────────────────


@router.get(
    "",
    response_model=PaginatedResponse[CommunityListResponse],
    summary="List Communities",
    description="List all communities with pagination, search, and filtering.",
)
async def list_communities(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, max_length=255),
    is_active: bool | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
    _user: dict | None = Depends(get_optional_user),
) -> PaginatedResponse[CommunityListResponse]:
    service = CommunityService(db)
    result = await service.list_communities(
        page=page,
        per_page=per_page,
        search=search,
        is_active=is_active,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return PaginatedResponse(data=result["items"], meta=result["meta"])


@router.get(
    "/my",
    response_model=ApiResponse[list[CommunityListResponse]],
    summary="My Communities",
    description="List communities the current user belongs to.",
)
async def my_communities(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[list[CommunityListResponse]]:
    service = CommunityService(db)
    result = await service.get_my_communities(user_id)
    return ApiResponse(data=result)


@router.get(
    "/slug/{slug}",
    response_model=ApiResponse[CommunityResponse],
    summary="Get Community by Slug",
    description="Public endpoint to look up a community by its URL slug.",
)
async def get_community_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[CommunityResponse]:
    service = CommunityService(db)
    result = await service.get_community_by_slug(slug)
    return ApiResponse(data=result)


@router.get(
    "/{community_id}",
    response_model=ApiResponse[CommunityResponse],
    summary="Get Community",
    description="Get full community details by ID.",
)
async def get_community(
    community_id: UUID,
    db: AsyncSession = Depends(get_db),
    _user: dict | None = Depends(get_optional_user),
) -> ApiResponse[CommunityResponse]:
    service = CommunityService(db)
    result = await service.get_community(community_id)
    return ApiResponse(data=result)


# ── Update ───────────────────────────────────────────────────────────────


@router.patch(
    "/{community_id}",
    response_model=ApiResponse[CommunityResponse],
    summary="Update Community",
    description="Partially update community details.",
    dependencies=[Depends(RequirePermissions(Permission.COMMUNITY_UPDATE))],
)
async def update_community(
    community_id: UUID,
    body: CommunityUpdateSchema,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[CommunityResponse]:
    service = CommunityService(db)
    result = await service.update_community(community_id, body, updated_by=user_id)
    return ApiResponse(data=result)


@router.put(
    "/{community_id}/settings",
    response_model=ApiResponse[CommunityResponse],
    summary="Update Settings",
    description="Update community configuration settings (merged with existing).",
    dependencies=[Depends(RequirePermissions(Permission.SETTINGS_UPDATE))],
)
async def update_settings(
    community_id: UUID,
    body: CommunitySettingsSchema,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[CommunityResponse]:
    service = CommunityService(db)
    result = await service.update_settings(community_id, body, updated_by=user_id)
    return ApiResponse(data=result)


# ── Activate / Deactivate ────────────────────────────────────────────────


@router.post(
    "/{community_id}/activate",
    response_model=ApiResponse[dict],
    summary="Activate Community",
    dependencies=[Depends(RequirePermissions(Permission.COMMUNITY_UPDATE))],
)
async def activate_community(
    community_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    service = CommunityService(db)
    result = await service.activate_community(community_id, updated_by=user_id)
    return ApiResponse(data=result)


@router.post(
    "/{community_id}/deactivate",
    response_model=ApiResponse[dict],
    summary="Deactivate Community",
    dependencies=[Depends(RequirePermissions(Permission.COMMUNITY_UPDATE))],
)
async def deactivate_community(
    community_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    service = CommunityService(db)
    result = await service.deactivate_community(community_id, updated_by=user_id)
    return ApiResponse(data=result)


# ── Delete ───────────────────────────────────────────────────────────────


@router.delete(
    "/{community_id}",
    response_model=ApiResponse[dict],
    summary="Delete Community",
    description="Soft-delete a community. Super Admin only.",
    dependencies=[Depends(RequirePermissions(Permission.COMMUNITY_DELETE))],
)
async def delete_community(
    community_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    service = CommunityService(db)
    result = await service.delete_community(community_id, deleted_by=user_id)
    return ApiResponse(data=result)


# ── Stats ────────────────────────────────────────────────────────────────


@router.get(
    "/{community_id}/stats",
    response_model=ApiResponse[CommunityStatsResponse],
    summary="Community Stats",
    description="Get dashboard-level statistics for a community.",
    dependencies=[Depends(RequirePermissions(Permission.COMMUNITY_READ))],
)
async def get_community_stats(
    community_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[CommunityStatsResponse]:
    service = CommunityService(db)
    result = await service.get_community_stats(community_id)
    return ApiResponse(data=result)


# ── Invite ───────────────────────────────────────────────────────────────


@router.post(
    "/{community_id}/invite",
    response_model=ApiResponse[dict],
    summary="Invite Member",
    description="Invite a user to join the community by mobile number.",
    dependencies=[Depends(RequirePermissions(Permission.MEMBER_CREATE))],
)
async def invite_member(
    community_id: UUID,
    body: InviteMemberSchema,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    service = CommunityService(db)
    result = await service.invite_member(
        community_id=community_id,
        mobile=body.mobile,
        role_name=body.role,
        full_name=body.full_name,
        invited_by=user_id,
    )
    return ApiResponse(data=result)
