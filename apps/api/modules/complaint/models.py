"""
ApnaSamaj – Complaint Models

Defines the ticketing system for member issues, suggestions, or disputes.
"""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.api.core.base_model import BaseModel

if TYPE_CHECKING:
    from apps.api.modules.committee.models import Committee
    from apps.api.modules.member.models import Member


class ComplaintStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class ComplaintPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Complaint(BaseModel):
    """
    A ticket raised by a member.
    It can be assigned to a specific committee for resolution.
    """

    __tablename__ = "complaints"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[ComplaintStatus] = mapped_column(default=ComplaintStatus.OPEN)
    priority: Mapped[ComplaintPriority] = mapped_column(default=ComplaintPriority.MEDIUM)

    # Who raised it
    reporter_id: Mapped[UUID] = mapped_column(ForeignKey("members.id"), nullable=False)

    # Which committee is handling it (optional)
    assigned_committee_id: Mapped[UUID | None] = mapped_column(ForeignKey("committees.id"), nullable=True)

    # Resolution notes
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    reporter: Mapped[Member] = relationship()
    assigned_committee: Mapped[Committee] = relationship()
