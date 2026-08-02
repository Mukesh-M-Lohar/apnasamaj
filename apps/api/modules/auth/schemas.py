"""
ApnaSamaj – Auth Pydantic Schemas

Request and response models for all authentication endpoints.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import Field, field_validator

from apps.api.core.base_schema import BaseSchema


# ── OTP Request / Verify ─────────────────────────────────────────────────

class OTPRequestSchema(BaseSchema):
    """POST /auth/otp/request"""

    mobile: str = Field(..., min_length=10, max_length=15, description="Mobile number with country code")

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        cleaned = v.strip().replace(" ", "").replace("-", "")
        if not cleaned.replace("+", "").isdigit():
            raise ValueError("Mobile number must contain only digits and optional leading +")
        return cleaned


class OTPVerifySchema(BaseSchema):
    """POST /auth/otp/verify"""

    mobile: str = Field(..., min_length=10, max_length=15)
    otp: str = Field(..., min_length=4, max_length=8)
    device_name: str | None = Field(default=None, max_length=255)
    device_type: str | None = Field(default=None, max_length=50)  # mobile, web, tablet
    os: str | None = Field(default=None, max_length=100)
    browser: str | None = Field(default=None, max_length=100)
    tenant_id: UUID | None = Field(default=None, description="Optional tenant to log into")

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        cleaned = v.strip().replace(" ", "").replace("-", "")
        if not cleaned.replace("+", "").isdigit():
            raise ValueError("Mobile number must contain only digits and optional leading +")
        return cleaned


# ── Token Responses ──────────────────────────────────────────────────────

class TokenResponse(BaseSchema):
    """Returned after successful OTP verification or token refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: "UserResponse"
    tenant: "TenantBriefResponse | None" = None


class RefreshTokenRequest(BaseSchema):
    """POST /auth/token/refresh"""

    refresh_token: str


# ── User Response ────────────────────────────────────────────────────────

class UserResponse(BaseSchema):
    """User profile in auth responses."""

    id: UUID
    mobile: str
    email: str | None = None
    full_name: str | None = None
    avatar_url: str | None = None
    is_verified: bool = False
    is_super_admin: bool = False
    roles: list[str] = Field(default_factory=list)
    created_at: datetime


# ── Tenant Brief ─────────────────────────────────────────────────────────

class TenantBriefResponse(BaseSchema):
    """Minimal tenant info returned with auth tokens."""

    id: UUID
    name: str
    slug: str
    logo_url: str | None = None


# ── Session / Device ─────────────────────────────────────────────────────

class SessionResponse(BaseSchema):
    """Active session / device info."""

    id: UUID
    device_name: str | None = None
    device_type: str | None = None
    os: str | None = None
    browser: str | None = None
    ip_address: str | None = None
    is_revoked: bool = False
    last_used_at: datetime | None = None
    created_at: datetime


class UserProfileResponse(BaseSchema):
    """GET /auth/me – full profile with tenants."""

    id: UUID
    mobile: str
    email: str | None = None
    full_name: str | None = None
    avatar_url: str | None = None
    is_verified: bool
    is_super_admin: bool
    tenants: list[TenantBriefResponse] = Field(default_factory=list)
    created_at: datetime


# ── OTP Response ─────────────────────────────────────────────────────────

class OTPResponse(BaseSchema):
    """Response after OTP is sent."""

    message: str = "OTP sent successfully"
    expires_in: int  # seconds
    mobile: str


# ── Social Login Scaffold ───────────────────────────────────────────────

class GoogleLoginSchema(BaseSchema):
    """POST /auth/google"""

    id_token: str
    device_name: str | None = None
    device_type: str | None = None
    tenant_id: UUID | None = None


class AppleLoginSchema(BaseSchema):
    """POST /auth/apple"""

    identity_token: str
    authorization_code: str
    full_name: str | None = None
    device_name: str | None = None
    device_type: str | None = None
    tenant_id: UUID | None = None
