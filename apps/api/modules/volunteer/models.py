"""
ApnaSamaj – Volunteer Model

Tracks volunteer skills, availability, event assignments,
attendance, hours, and performance.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from apps.api.core.base_model import BaseModel


class Volunteer(BaseModel):
    """A volunteer profile linked to a community member."""

    __tablename__ = "volunteers"

    member_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("members.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    skills: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # ["cooking", "decoration", ...]
    availability: Mapped[str | None] = mapped_column(String(50), nullable=True)  # weekdays, weekends, anytime
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)  # active, inactive

    total_hours: Mapped[Decimal] = mapped_column(Numeric(8, 2), default=0, nullable=False)
    total_events: Mapped[int] = mapped_column(default=0, nullable=False)
    rating: Mapped[Decimal | None] = mapped_column(Numeric(3, 2), nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class VolunteerAssignment(BaseModel):
    """Assigns a volunteer to an event with role and attendance tracking."""

    __tablename__ = "volunteer_assignments"

    volunteer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("volunteers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    hours: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    attended: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"))
    check_in_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    check_out_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    certificate_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
