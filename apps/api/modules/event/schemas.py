"""
ApnaSamaj – Event Pydantic Schemas

Request/response models for community events, registrations, and check-ins.
"""

from __future__ import annotations

from datetime import date, datetime, time
from uuid import UUID

from pydantic import Field, field_validator

from apps.api.core.base_schema import BaseSchema


# ── Event ────────────────────────────────────────────────────────────────

class EventCreateSchema(BaseSchema):
    title: str = Field(..., min_length=3, max_length=255)
    description: str | None = None
    event_type: str = Field(..., max_length=50)
    
    start_date: date
    end_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    
    venue: str | None = Field(default=None, max_length=255)
    address: str | None = None
    maps_url: str | None = Field(default=None, max_length=512)
    
    is_online: bool = False
    online_url: str | None = Field(default=None, max_length=512)
    
    is_registration_open: bool = True
    max_attendees: int | None = None
    registration_deadline: datetime | None = None
    
    banner_url: str | None = Field(default=None, max_length=512)
    gallery_urls: dict | None = None
    
    status: str = Field(default="upcoming", max_length=20)
    organizer_id: UUID | None = None
    committee_id: UUID | None = None

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, end_date: date | None, info) -> date | None:
        if end_date and "start_date" in info.data:
            start_date = info.data["start_date"]
            if start_date and end_date < start_date:
                raise ValueError("end_date cannot be before start_date")
        return end_date


class EventUpdateSchema(BaseSchema):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_registration_open: bool | None = None
    status: str | None = Field(default=None, max_length=20)

    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, end_date: date | None, info) -> date | None:
        if end_date and "start_date" in info.data:
            start_date = info.data["start_date"]
            if start_date and end_date < start_date:
                raise ValueError("end_date cannot be before start_date")
        return end_date


class EventResponse(BaseSchema):
    id: UUID
    title: str
    description: str | None = None
    event_type: str
    
    start_date: date
    end_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    
    venue: str | None = None
    address: str | None = None
    maps_url: str | None = None
    
    is_online: bool
    online_url: str | None = None
    
    is_registration_open: bool
    max_attendees: int | None = None
    registration_deadline: datetime | None = None
    
    banner_url: str | None = None
    gallery_urls: dict | None = None
    qr_code_url: str | None = None
    
    status: str
    organizer_id: UUID | None = None
    committee_id: UUID | None = None
    
    created_at: datetime
    updated_at: datetime


# ── Event Registrations (RSVP) ───────────────────────────────────────────

class EventRegistrationSchema(BaseSchema):
    """Payload to register a member for an event."""
    member_id: UUID
    guests: int = Field(default=0, ge=0)
    notes: str | None = None


class EventCheckInSchema(BaseSchema):
    """Payload to check a member into an event."""
    member_id: UUID
    check_in_method: str = Field(default="manual", max_length=20)


class EventRegistrationResponse(BaseSchema):
    id: UUID
    event_id: UUID
    member_id: UUID
    status: str
    checked_in_at: datetime | None = None
    check_in_method: str | None = None
    guests: int
    notes: str | None = None
    
    created_at: datetime
