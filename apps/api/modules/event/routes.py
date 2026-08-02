"""
ApnaSamaj – Event API Routes

All event endpoints scoped to the current tenant:
  • POST   /events                   – Create event
  • GET    /events                   – List events
  • GET    /events/{id}              – Get event details
  • PATCH  /events/{id}              – Update event
  • DELETE /events/{id}              – Delete event
  • GET    /events/{id}/attendees    – List registered members
  • POST   /events/{id}/register     – RSVP for an event
  • POST   /events/{id}/check-in     – Mark attendance
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.base_schema import ApiResponse, PaginatedResponse
from apps.api.core.database import get_db
from apps.api.core.dependencies import get_current_tenant_id, get_current_user_id
from apps.api.core.permissions import Permission, RequirePermissions
from apps.api.modules.event.schemas import (
    EventCheckInSchema,
    EventCreateSchema,
    EventRegistrationResponse,
    EventRegistrationSchema,
    EventResponse,
    EventUpdateSchema,
)
from apps.api.modules.event.service import EventService

router = APIRouter(prefix="/events", tags=["Events"])


# ── Create ───────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=ApiResponse[EventResponse],
    summary="Create Event",
    dependencies=[Depends(RequirePermissions(Permission.EVENT_CREATE))],
)
async def create_event(
    body: EventCreateSchema,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[EventResponse]:
    service = EventService(db, tenant_id)
    result = await service.create_event(body, created_by=user_id)
    return ApiResponse(data=result)


# ── Read ─────────────────────────────────────────────────────────────────

@router.get(
    "",
    response_model=PaginatedResponse[EventResponse],
    summary="List Events",
    dependencies=[Depends(RequirePermissions(Permission.EVENT_READ))],
)
async def list_events(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    event_type: str | None = Query(default=None),
    search: str | None = Query(default=None, max_length=255),
    sort_by: str = Query(default="start_date"),
    sort_order: str = Query(default="asc", pattern="^(asc|desc)$"),
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[EventResponse]:
    service = EventService(db, tenant_id)
    result = await service.list_events(
        page=page,
        per_page=per_page,
        status=status,
        event_type=event_type,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return PaginatedResponse(data=result["items"], meta=result["meta"])


@router.get(
    "/{event_id}",
    response_model=ApiResponse[EventResponse],
    summary="Get Event",
    dependencies=[Depends(RequirePermissions(Permission.EVENT_READ))],
)
async def get_event(
    event_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[EventResponse]:
    service = EventService(db, tenant_id)
    result = await service.get_event(event_id)
    return ApiResponse(data=result)


# ── Update ───────────────────────────────────────────────────────────────

@router.patch(
    "/{event_id}",
    response_model=ApiResponse[EventResponse],
    summary="Update Event",
    dependencies=[Depends(RequirePermissions(Permission.EVENT_UPDATE))],
)
async def update_event(
    event_id: UUID,
    body: EventUpdateSchema,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[EventResponse]:
    service = EventService(db, tenant_id)
    result = await service.update_event(event_id, body, updated_by=user_id)
    return ApiResponse(data=result)


# ── Delete ───────────────────────────────────────────────────────────────

@router.delete(
    "/{event_id}",
    response_model=ApiResponse[dict],
    summary="Delete Event",
    dependencies=[Depends(RequirePermissions(Permission.EVENT_DELETE))],
)
async def delete_event(
    event_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    service = EventService(db, tenant_id)
    result = await service.delete_event(event_id, deleted_by=user_id)
    return ApiResponse(data=result)


# ── Registrations & Check-In ─────────────────────────────────────────────

@router.get(
    "/{event_id}/attendees",
    response_model=ApiResponse[list[EventRegistrationResponse]],
    summary="List Event Attendees",
    dependencies=[Depends(RequirePermissions(Permission.EVENT_READ))],
)
async def list_attendees(
    event_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[list[EventRegistrationResponse]]:
    service = EventService(db, tenant_id)
    result = await service.get_attendees(event_id)
    return ApiResponse(data=result)


@router.post(
    "/{event_id}/register",
    response_model=ApiResponse[EventRegistrationResponse],
    summary="RSVP for Event",
    description="Register a member for the event.",
    dependencies=[Depends(RequirePermissions(Permission.EVENT_UPDATE))],
)
async def register_member(
    event_id: UUID,
    body: EventRegistrationSchema,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[EventRegistrationResponse]:
    service = EventService(db, tenant_id)
    result = await service.register_member(event_id, body, created_by=user_id)
    return ApiResponse(data=result)


@router.post(
    "/{event_id}/check-in",
    response_model=ApiResponse[EventRegistrationResponse],
    summary="Event Check-In",
    description="Mark a registered member as attended.",
    dependencies=[Depends(RequirePermissions(Permission.EVENT_UPDATE))],
)
async def check_in_member(
    event_id: UUID,
    body: EventCheckInSchema,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[EventRegistrationResponse]:
    service = EventService(db, tenant_id)
    result = await service.check_in_member(event_id, body, updated_by=user_id)
    return ApiResponse(data=result)
