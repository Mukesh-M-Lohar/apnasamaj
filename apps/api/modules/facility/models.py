"""
ApnaSamaj – Facility Models

Defines community assets (halls, sports courts) and their booking ledger.
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.api.core.base_model import BaseModel

if TYPE_CHECKING:
    from apps.api.modules.member.models import Member


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Facility(BaseModel):
    """A physical community asset that can be booked."""

    __tablename__ = "facilities"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    capacity: Mapped[int] = mapped_column(default=0)
    hourly_rate: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    is_active: Mapped[bool] = mapped_column(default=True)

    bookings: Mapped[list[FacilityBooking]] = relationship(back_populates="facility")


class FacilityBooking(BaseModel):
    """A reservation of a facility by a member."""

    __tablename__ = "facility_bookings"

    facility_id: Mapped[UUID] = mapped_column(ForeignKey("facilities.id"), nullable=False)
    booked_by_id: Mapped[UUID] = mapped_column(ForeignKey("members.id"), nullable=False)

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    status: Mapped[BookingStatus] = mapped_column(default=BookingStatus.PENDING)

    # Financial tie-in
    total_cost: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    # Relationships
    facility: Mapped[Facility] = relationship(back_populates="bookings")
    booked_by: Mapped[Member] = relationship()
