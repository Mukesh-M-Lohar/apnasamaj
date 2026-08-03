"""
ApnaSamaj – Notification Service

Business logic for managing broadcasting events.
"""

from __future__ import annotations

import logging
import math
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.modules.notification.models import NotificationStatus
from apps.api.modules.notification.repository import NotificationRepository
from apps.api.modules.notification.schemas import (
    NotificationCreateSchema,
    NotificationResponse,
)

logger = logging.getLogger(__name__)


class NotificationService:
    """Business logic for broadcasting and notifications."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self._repo = NotificationRepository(session, tenant_id)
        self.tenant_id = tenant_id

    async def broadcast_message(
        self,
        data: NotificationCreateSchema,
        sender_id: UUID,
    ) -> NotificationResponse:
        """Queue a broadcast message."""
        payload = data.model_dump(exclude_none=True)
        payload["sender_id"] = sender_id

        # In a real app, this is where you'd trigger a Celery task to send
        # via Firebase (Push), Twilio (SMS), or SendGrid (Email).
        # We simulate the queuing here by setting status to SENT immediately.
        payload["status"] = NotificationStatus.SENT

        notification = await self._repo.create(
            data=payload,
            created_by=sender_id,
        )
        logger.info("Broadcast queued by member: %s via %s", sender_id, data.channel)
        return NotificationResponse.model_validate(notification)

    async def list_broadcasts(
        self,
        page: int = 1,
        per_page: int = 20,
    ) -> dict[str, Any]:
        """List past broadcast messages."""
        offset = (page - 1) * per_page
        notifications, total = await self._repo.get_all_paginated(
            offset=offset,
            limit=per_page,
        )

        total_pages = math.ceil(total / per_page) if per_page > 0 else 0
        items = [NotificationResponse.model_validate(n) for n in notifications]

        return {
            "items": items,
            "meta": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            },
        }
