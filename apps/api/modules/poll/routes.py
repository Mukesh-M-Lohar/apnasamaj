"""
ApnaSamaj – Poll API Routes

Endpoints for managing and voting on community polls.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.base_schema import ApiResponse, PaginatedResponse
from apps.api.core.database import get_db
from apps.api.core.dependencies import get_current_tenant_id, get_current_user_id
from apps.api.core.permissions import Permission, RequirePermissions
from apps.api.modules.poll.schemas import (
    PollCreateSchema,
    PollResponse,
    PollVoteSchema,
)
from apps.api.modules.poll.service import PollService

router = APIRouter(prefix="/polls", tags=["Polling"])


@router.post(
    "",
    response_model=ApiResponse[PollResponse],
    summary="Create Poll",
    dependencies=[Depends(RequirePermissions(Permission.COMMUNITY_CREATE))],
)
async def create_poll(
    body: PollCreateSchema,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[PollResponse]:
    service = PollService(db, tenant_id)
    result = await service.create_poll(body, created_by=user_id)
    return ApiResponse(data=result)


@router.get(
    "",
    response_model=PaginatedResponse[PollResponse],
    summary="List Polls",
)
async def list_polls(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[PollResponse]:
    service = PollService(db, tenant_id)
    result = await service.list_polls(page=page, per_page=per_page)
    return PaginatedResponse(data=result["items"], meta=result["meta"])


@router.get(
    "/{poll_id}",
    response_model=ApiResponse[PollResponse],
    summary="Get Poll",
)
async def get_poll(
    poll_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[PollResponse]:
    service = PollService(db, tenant_id)
    result = await service.get_poll(poll_id)
    return ApiResponse(data=result)


@router.post(
    "/{poll_id}/vote",
    response_model=ApiResponse[dict],
    summary="Cast Vote",
)
async def cast_vote(
    poll_id: UUID,
    body: PollVoteSchema,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    service = PollService(db, tenant_id)
    # Again, treating user_id as member_id for simplicity
    result = await service.cast_vote(poll_id, body, member_id=user_id)
    return ApiResponse(data=result)
