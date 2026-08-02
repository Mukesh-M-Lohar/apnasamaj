"""
ApnaSamaj – Member Pydantic Schemas

Request/response models for community members.
"""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import Field, field_validator

from apps.api.core.base_schema import BaseSchema


# ── Create ───────────────────────────────────────────────────────────────

class MemberCreateSchema(BaseSchema):
    """POST /members – create a new member manually."""

    first_name: str = Field(..., min_length=1, max_length=100)
    middle_name: str | None = Field(default=None, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    gender: str | None = Field(default=None, max_length=20)
    date_of_birth: date | None = None
    anniversary_date: date | None = None

    occupation: str | None = Field(default=None, max_length=255)
    education: str | None = Field(default=None, max_length=255)
    company: str | None = Field(default=None, max_length=255)
    blood_group: str | None = Field(default=None, max_length=5)

    email: str | None = Field(default=None, max_length=255)
    mobile: str | None = Field(default=None, min_length=10, max_length=15)
    alternate_mobile: str | None = Field(default=None, max_length=15)

    address_line1: str | None = Field(default=None, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default="India", max_length=100)
    pincode: str | None = Field(default=None, max_length=10)

    emergency_contact_name: str | None = Field(default=None, max_length=255)
    emergency_contact_mobile: str | None = Field(default=None, max_length=15)
    emergency_contact_relation: str | None = Field(default=None, max_length=100)

    membership_number: str | None = Field(default=None, max_length=50)

    @field_validator("mobile", "alternate_mobile", "emergency_contact_mobile")
    @classmethod
    def validate_mobile(cls, v: str | None) -> str | None:
        if v is None:
            return None
        cleaned = v.strip().replace(" ", "").replace("-", "")
        if not cleaned.replace("+", "").isdigit():
            raise ValueError("Mobile number must contain only digits")
        return cleaned


# ── Update ───────────────────────────────────────────────────────────────

class MemberUpdateSchema(BaseSchema):
    """PATCH /members/{id} – partial update."""

    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    middle_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    photo_url: str | None = Field(default=None, max_length=512)
    gender: str | None = Field(default=None, max_length=20)
    date_of_birth: date | None = None
    anniversary_date: date | None = None

    occupation: str | None = Field(default=None, max_length=255)
    education: str | None = Field(default=None, max_length=255)
    company: str | None = Field(default=None, max_length=255)
    blood_group: str | None = Field(default=None, max_length=5)

    email: str | None = Field(default=None, max_length=255)
    mobile: str | None = Field(default=None, min_length=10, max_length=15)
    alternate_mobile: str | None = Field(default=None, max_length=15)

    address_line1: str | None = Field(default=None, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    pincode: str | None = Field(default=None, max_length=10)

    emergency_contact_name: str | None = Field(default=None, max_length=255)
    emergency_contact_mobile: str | None = Field(default=None, max_length=15)
    emergency_contact_relation: str | None = Field(default=None, max_length=100)

    status: str | None = Field(default=None, max_length=20)
    notes: str | None = None

    @field_validator("mobile", "alternate_mobile", "emergency_contact_mobile")
    @classmethod
    def validate_mobile(cls, v: str | None) -> str | None:
        if v is None:
            return None
        cleaned = v.strip().replace(" ", "").replace("-", "")
        if not cleaned.replace("+", "").isdigit():
            raise ValueError("Mobile number must contain only digits")
        return cleaned


# ── Response ─────────────────────────────────────────────────────────────

class MemberResponse(BaseSchema):
    """Full member detail response."""

    id: UUID
    user_id: UUID | None = None
    family_id: UUID | None = None

    first_name: str
    middle_name: str | None = None
    last_name: str
    photo_url: str | None = None
    gender: str | None = None
    date_of_birth: date | None = None
    anniversary_date: date | None = None

    occupation: str | None = None
    education: str | None = None
    company: str | None = None
    blood_group: str | None = None

    email: str | None = None
    mobile: str | None = None
    alternate_mobile: str | None = None

    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    pincode: str | None = None

    emergency_contact_name: str | None = None
    emergency_contact_mobile: str | None = None
    emergency_contact_relation: str | None = None

    status: str
    membership_number: str | None = None

    created_at: datetime
    updated_at: datetime

    @property
    def full_name(self) -> str:
        parts = [self.first_name, self.middle_name, self.last_name]
        return " ".join(p for p in parts if p)


class MemberListResponse(BaseSchema):
    """Compact member item for directory listings."""

    id: UUID
    first_name: str
    last_name: str
    photo_url: str | None = None
    mobile: str | None = None
    blood_group: str | None = None
    occupation: str | None = None
    city: str | None = None
    status: str

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


# ── Bulk Import ──────────────────────────────────────────────────────────

class BulkImportError(BaseSchema):
    row: int
    error: str
    data: dict | None = None

class BulkImportResultResponse(BaseSchema):
    """Result of a bulk import operation."""
    total_rows: int
    success_count: int
    error_count: int
    errors: list[BulkImportError] = Field(default_factory=list)
