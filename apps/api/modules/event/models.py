"""
ApnaSamaj – Event Models

Event management with registration, attendance, QR check-in, galleries,
volunteer assignments, and announcements.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, time

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, Time, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from apps.api.core.base_model import BaseModel


class Event(BaseModel):
    """A community event (festival, meeting, ceremony, etc.)."""

    __tablename__ = "events"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)  # festival, meeting, ceremony, social, other

    # ── Schedule ─────────────────────────────────────────────────────────
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    end_time: Mapped[time | None] = mapped_column(Time, nullable=True)

    # ── Location ─────────────────────────────────────────────────────────
    venue: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    maps_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"), nullable=False)
    online_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # ── Registration ─────────────────────────────────────────────────────
    is_registration_open: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))
    max_attendees: Mapped[int | None] = mapped_column(Integer, nullable=True)
    registration_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # ── Media ────────────────────────────────────────────────────────────
    banner_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    gallery_urls: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # list of image URLs

    # ── QR Check-in ──────────────────────────────────────────────────────
    qr_code_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # ── Status ───────────────────────────────────────────────────────────
    status: Mapped[str] = mapped_column(String(20), default="upcoming", nullable=False)
    # upcoming, ongoing, completed, cancelled

    # ── Organiser ────────────────────────────────────────────────────────
    organizer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("members.id", ondelete="SET NULL"),
        nullable=True,
    )
    committee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("committees.id", ondelete="SET NULL"),
        nullable=True,
    )


class EventRegistration(BaseModel):
    """A member's registration for an event."""

    __tablename__ = "event_registrations"

    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    member_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("members.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(String(20), default="registered", nullable=False)
    # registered, attended, no_show, cancelled

    checked_in_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    check_in_method: Mapped[str | None] = mapped_column(String(20), nullable=True)  # qr, manual

    guests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
