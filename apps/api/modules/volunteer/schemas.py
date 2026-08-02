"""
ApnaSamaj – Volunteer Pydantic Schemas

Request/response models for volunteer profiles and event assignments.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field

from apps.api.core.base_schema import BaseSchema


# ── Volunteer Profile ────────────────────────────────────────────────────

class VolunteerCreateSchema(BaseSchema):
    member_id: UUID
    skills: list[str] | None = Field(default_factory=list)
    availability: str | None = Field(default=None, max_length=50)
    notes: str | None = None
    status: str = Field(default="active", max_length=20)


class VolunteerUpdateSchema(BaseSchema):
    skills: list[str] | None = None
    availability: str | None = Field(default=None, max_length=50)
    notes: str | None = None
    status: str | None = Field(default=None, max_length=20)
    rating: Decimal | None = Field(default=None, ge=0, le=5, decimal_places=2)


class VolunteerResponse(BaseSchema):
    id: UUID
    member_id: UUID
    skills: list[str] | None = Field(default_factory=list)
    availability: str | None = None
    status: str
    
    total_hours: Decimal
    total_events: int
    rating: Decimal | None = None
    notes: str | None = None
    
    created_at: datetime
    updated_at: datetime


# ── Volunteer Assignments ────────────────────────────────────────────────

class VolunteerAssignmentCreateSchema(BaseSchema):
    event_id: UUID
    role: str | None = Field(default=None, max_length=100)


class VolunteerAssignmentUpdateSchema(BaseSchema):
    role: str | None = Field(default=None, max_length=100)
    attended: bool | None = None
    hours: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    feedback: str | None = None
    certificate_url: str | None = Field(default=None, max_length=512)
    # Check-in and check-out times can be passed if setting attended=True
    check_in_at: datetime | None = None
    check_out_at: datetime | None = None


class VolunteerAssignmentResponse(BaseSchema):
    id: UUID
    volunteer_id: UUID
    event_id: UUID
    
    role: str | None = None
    hours: Decimal | None = None
    attended: bool
    
    check_in_at: datetime | None = None
    check_out_at: datetime | None = None
    
    feedback: str | None = None
    certificate_url: str | None = None
    
    created_at: datetime
    updated_at: datetime
