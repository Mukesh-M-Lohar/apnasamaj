"""
ApnaSamaj – Community (Tenant) Pydantic Schemas

Request/response models for community CRUD and onboarding.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import Field, field_validator

from apps.api.core.base_schema import BaseSchema


# ── Create ───────────────────────────────────────────────────────────────

class CommunityCreateSchema(BaseSchema):
    """POST /communities – create a new community."""

    name: str = Field(..., min_length=2, max_length=255)
    slug: str = Field(..., min_length=2, max_length=255, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    description: str | None = Field(default=None, max_length=2000)
    logo_url: str | None = Field(default=None, max_length=512)

    # Contact
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    website: str | None = Field(default=None, max_length=512)

    # Address
    address_line1: str | None = Field(default=None, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    country: str = Field(default="India", max_length=100)
    pincode: str | None = Field(default=None, max_length=10)

    # Localization
    primary_language: str = Field(default="en", max_length=10)
    secondary_language: str | None = Field(default=None, max_length=10)
    timezone: str = Field(default="Asia/Kolkata", max_length=50)
    currency: str = Field(default="INR", max_length=3)

    # Social
    social_links: dict | None = None

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        return v.lower().strip()


# ── Update ───────────────────────────────────────────────────────────────

class CommunityUpdateSchema(BaseSchema):
    """PATCH /communities/{id} – partial update."""

    name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    logo_url: str | None = None

    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    website: str | None = Field(default=None, max_length=512)

    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    pincode: str | None = None

    primary_language: str | None = None
    secondary_language: str | None = None
    timezone: str | None = None
    currency: str | None = None

    social_links: dict | None = None
    settings: dict | None = None


# ── Settings ─────────────────────────────────────────────────────────────

class CommunitySettingsSchema(BaseSchema):
    """PUT /communities/{id}/settings – update community settings."""

    settings: dict


# ── Response ─────────────────────────────────────────────────────────────

class CommunityResponse(BaseSchema):
    """Full community detail response."""

    id: UUID
    name: str
    slug: str
    description: str | None = None
    logo_url: str | None = None

    email: str | None = None
    phone: str | None = None
    website: str | None = None

    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    pincode: str | None = None

    primary_language: str
    secondary_language: str | None = None
    timezone: str
    currency: str

    social_links: dict | None = None
    settings: dict | None = None

    is_active: bool
    created_at: datetime
    updated_at: datetime


class CommunityListResponse(BaseSchema):
    """Compact community item for list views."""

    id: UUID
    name: str
    slug: str
    logo_url: str | None = None
    city: str | None = None
    state: str | None = None
    is_active: bool
    member_count: int = 0
    created_at: datetime


# ── Onboarding ───────────────────────────────────────────────────────────

class CommunityOnboardSchema(BaseSchema):
    """
    POST /communities/onboard – create community + assign admin.

    Used when a new community registers on the platform.
    Creates the community AND assigns the current user as Community Admin.
    """

    community: CommunityCreateSchema
    admin_full_name: str | None = Field(default=None, max_length=255)


class CommunityOnboardResponse(BaseSchema):
    """Response after successful onboarding."""

    community: CommunityResponse
    role: str = "community_admin"
    message: str = "Community created successfully. You are now the Community Admin."


# ── Member Invite ────────────────────────────────────────────────────────

class InviteMemberSchema(BaseSchema):
    """POST /communities/{id}/invite – invite a user by mobile."""

    mobile: str = Field(..., min_length=10, max_length=15)
    role: str = Field(default="member", max_length=50)
    full_name: str | None = Field(default=None, max_length=255)

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        cleaned = v.strip().replace(" ", "").replace("-", "")
        if not cleaned.replace("+", "").isdigit():
            raise ValueError("Mobile number must contain only digits")
        return cleaned


class CommunityStatsResponse(BaseSchema):
    """GET /communities/{id}/stats – dashboard-level stats."""

    total_members: int = 0
    active_members: int = 0
    total_families: int = 0
    total_donations: int = 0
    total_events: int = 0
    total_volunteers: int = 0
    open_complaints: int = 0
