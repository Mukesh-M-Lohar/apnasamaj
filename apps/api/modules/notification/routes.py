"""
ApnaSamaj – Notification API Routes

Endpoints for broadcasting messages to the community.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.base_schema import ApiResponse, PaginatedResponse
from apps.api.core.database import get_db
from apps.api.core.dependencies import get_current_tenant_id, get_current_user_id
from apps.api.core.permissions import Permission, RequirePermissions
from apps.api.modules.notification.schemas import (
    NotificationCreateSchema,
    NotificationResponse,
)
from apps.api.modules.notification.service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post(
    "/broadcast",
    response_model=ApiResponse[NotificationResponse],
    summary="Broadcast Notification",
    description="Send a message (Push, SMS, Email) to the community or a specific committee.",
    dependencies=[Depends(RequirePermissions(Permission.COMMUNITY_UPDATE))],
)
async def broadcast_message(
    body: NotificationCreateSchema,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[NotificationResponse]:
    service = NotificationService(db, tenant_id)
    result = await service.broadcast_message(body, sender_id=user_id)
    return ApiResponse(data=result)


@router.get(
    "",
    response_model=PaginatedResponse[NotificationResponse],
    summary="List Broadcasts",
    dependencies=[Depends(RequirePermissions(Permission.COMMUNITY_UPDATE))],
)
async def list_broadcasts(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[NotificationResponse]:
    service = NotificationService(db, tenant_id)
    result = await service.list_broadcasts(page=page, per_page=per_page)
    return PaginatedResponse(data=result["items"], meta=result["meta"])
