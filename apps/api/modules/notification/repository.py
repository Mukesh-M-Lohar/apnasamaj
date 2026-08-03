"""
ApnaSamaj – Notification Repository

Database operations for handling broadcast messages.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.modules.notification.models import Notification


class NotificationRepository:
    """Handles notification DB operations scoped to a tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self._session = session
        self.tenant_id = tenant_id

    def _base_query(self) -> Select:
        return select(Notification).where(
            Notification.tenant_id == self.tenant_id,
            Notification.is_deleted == False,  # noqa: E712
        )

    async def create(self, data: dict[str, Any], created_by: UUID | None = None) -> Notification:
        notification = Notification(
            tenant_id=self.tenant_id,
            created_by=created_by,
            updated_by=created_by,
            **data,
        )
        self._session.add(notification)
        await self._session.flush()
        await self._session.refresh(notification)
        return notification

    async def get_by_id(self, notification_id: UUID) -> Notification | None:
        stmt = self._base_query().where(Notification.id == notification_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_paginated(
        self,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Notification], int]:
        stmt = self._base_query()
        count_stmt = (
            select(func.count())
            .select_from(Notification)
            .where(
                Notification.tenant_id == self.tenant_id,
                Notification.is_deleted == False,  # noqa: E712
            )
        )

        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = stmt.order_by(Notification.created_at.desc())
        stmt = stmt.offset(offset).limit(limit)

        result = await self._session.execute(stmt)
        notifications = list(result.scalars().all())

        return notifications, total
