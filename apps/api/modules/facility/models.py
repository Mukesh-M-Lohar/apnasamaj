"""
ApnaSamaj – Facility Models

Defines community assets (halls, sports courts) and their booking ledger.
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, String, Text
from sqlalchemy import Column, Numeric, DateTime

from apps.api.core.models.base import BaseModel

if TYPE_CHECKING:
    from apps.api.modules.member.models import Member


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Facility(BaseModel, table=True):
    """A physical community asset that can be booked."""
    __tablename__ = "facilities"

    name: str = Field(sa_column=Column(String(255), nullable=False))
    description: str | None = Field(default=None, sa_column=Column(Text))
    
    capacity: int = Field(default=0)
    hourly_rate: float | None = Field(default=None, sa_column=Column(Numeric(10, 2)))
    
    is_active: bool = Field(default=True)

    bookings: list["FacilityBooking"] = Relationship(back_populates="facility")


class FacilityBooking(BaseModel, table=True):
    """A reservation of a facility by a member."""
    __tablename__ = "facility_bookings"

    facility_id: UUID = Field(foreign_key="facilities.id", nullable=False)
    booked_by_id: UUID = Field(foreign_key="members.id", nullable=False)
    
    start_time: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    end_time: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    
    status: BookingStatus = Field(default=BookingStatus.PENDING)
    
    # Financial tie-in
    total_cost: float | None = Field(default=None, sa_column=Column(Numeric(10, 2)))
    
    # Relationships
    facility: Facility = Relationship(back_populates="bookings")
    booked_by: "Member" = Relationship()
