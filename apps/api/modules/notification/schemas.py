"""
ApnaSamaj – Notification Schemas

Pydantic models for request validation and response serialization.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from apps.api.core.base_schema import BaseResponse
from apps.api.modules.notification.models import NotificationChannel, NotificationStatus


class NotificationCreateSchema(BaseModel):
    title: str = Field(..., max_length=255)
    message: str
    channel: NotificationChannel = Field(default=NotificationChannel.PUSH)
    target_committee_id: UUID | None = None


class NotificationResponse(BaseResponse):
    title: str
    message: str
    channel: NotificationChannel
    status: NotificationStatus
    target_committee_id: UUID | None
    provider_reference: str | None
    sender_id: UUID | None
    
    model_config = ConfigDict(from_attributes=True)
