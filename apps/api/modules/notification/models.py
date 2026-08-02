"""
ApnaSamaj – Notification Models

Defines the broadcasting channels (Push, SMS, Email) and their logs.
"""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, String, Text
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

from apps.api.core.models.base import BaseModel

if TYPE_CHECKING:
    from apps.api.modules.member.models import Member


class NotificationChannel(str, enum.Enum):
    PUSH = "push"
    SMS = "sms"
    EMAIL = "email"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class Notification(BaseModel, table=True):
    """A broadcast message sent to members."""
    __tablename__ = "notifications"

    title: str = Field(sa_column=Column(String(255), nullable=False))
    message: str = Field(sa_column=Column(Text, nullable=False))
    
    channel: NotificationChannel = Field(default=NotificationChannel.PUSH)
    status: NotificationStatus = Field(default=NotificationStatus.PENDING)

    # Optional targeting: if null, it's a tenant-wide broadcast.
    # Otherwise, it might target a specific committee or list of members.
    target_committee_id: UUID | None = Field(default=None, foreign_key="committees.id")
    
    # Store provider response (e.g. FCM message ID or SendGrid ID)
    provider_reference: str | None = Field(default=None, sa_column=Column(String(255)))
    
    # Who triggered the broadcast
    sender_id: UUID | None = Field(default=None, foreign_key="members.id")
