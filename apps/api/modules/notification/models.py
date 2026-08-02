"""
ApnaSamaj – Notification Models

Defines the broadcasting channels (Push, SMS, Email) and their logs.
"""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from apps.api.core.base_model import BaseModel

if TYPE_CHECKING:
    pass


class NotificationChannel(str, enum.Enum):
    PUSH = "push"
    SMS = "sms"
    EMAIL = "email"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class Notification(BaseModel):
    """A broadcast message sent to members."""

    __tablename__ = "notifications"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    channel: Mapped[NotificationChannel] = mapped_column(
        default=NotificationChannel.PUSH
    )
    status: Mapped[NotificationStatus] = mapped_column(
        default=NotificationStatus.PENDING
    )

    # Optional targeting: if null, it's a tenant-wide broadcast.
    # Otherwise, it might target a specific committee or list of members.
    target_committee_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("committees.id"), nullable=True
    )

    # Store provider response (e.g. FCM message ID or SendGrid ID)
    provider_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Who triggered the broadcast
    sender_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("members.id"), nullable=True
    )
