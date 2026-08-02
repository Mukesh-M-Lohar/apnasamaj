"""
ApnaSamaj – Complaint Models

Defines the ticketing system for member issues, suggestions, or disputes.
"""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, String, Text
from sqlalchemy import Column

from apps.api.core.models.base import BaseModel

if TYPE_CHECKING:
    from apps.api.modules.member.models import Member
    from apps.api.modules.committee.models import Committee


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


class Complaint(BaseModel, table=True):
    """
    A ticket raised by a member.
    It can be assigned to a specific committee for resolution.
    """
    __tablename__ = "complaints"

    title: str = Field(sa_column=Column(String(255), nullable=False))
    description: str = Field(sa_column=Column(Text, nullable=False))
    
    status: ComplaintStatus = Field(default=ComplaintStatus.OPEN)
    priority: ComplaintPriority = Field(default=ComplaintPriority.MEDIUM)

    # Who raised it
    reporter_id: UUID = Field(foreign_key="members.id", nullable=False)
    
    # Which committee is handling it (optional)
    assigned_committee_id: UUID | None = Field(default=None, foreign_key="committees.id")

    # Resolution notes
    resolution_notes: str | None = Field(default=None, sa_column=Column(Text, nullable=True))

    # Relationships
    reporter: "Member" = Relationship()
    assigned_committee: "Committee" = Relationship()
