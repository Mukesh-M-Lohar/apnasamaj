"""
ApnaSamaj – Base Pydantic Schemas

Shared request/response schemas used across all modules.

Design decisions:
  • All responses wrapped in a standard envelope { success, data, meta }.
  • Pagination metadata returned in `meta` for list endpoints.
  • ConfigDict with from_attributes=True so schemas work with ORM objects.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


# ── Standard API Envelope ────────────────────────────────────────────────


class ApiResponse(BaseModel, Generic[T]):
    """Wrap every API response for consistent frontend parsing."""

    success: bool = True
    data: T | None = None
    meta: dict[str, Any] = Field(default_factory=dict)


class PaginationMeta(BaseModel):
    """Pagination metadata returned in ApiResponse.meta."""

    page: int = 1
    per_page: int = 20
    total: int = 0
    total_pages: int = 0


class PaginatedResponse(BaseModel, Generic[T]):
    """List response with pagination."""

    success: bool = True
    data: list[T] = Field(default_factory=list)
    meta: PaginationMeta = Field(default_factory=PaginationMeta)


# ── Common Mixins ────────────────────────────────────────────────────────


class TimestampMixin(BaseModel):
    """Read-only audit timestamps."""

    created_at: datetime
    updated_at: datetime


class TenantMixin(BaseModel):
    """Include tenant_id in response when needed."""

    tenant_id: UUID


class BaseSchema(BaseModel):
    """Base schema that all domain schemas should inherit from."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class BaseResponseSchema(BaseSchema, TimestampMixin):
    """Base response schema with id + timestamps."""

    id: UUID


# ── Request Helpers ──────────────────────────────────────────────────────


class PaginationParams(BaseModel):
    """Query parameters for paginated endpoints."""

    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page


class SortParams(BaseModel):
    """Query parameters for sorting."""

    sort_by: str = "created_at"
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


class FilterParams(BaseModel):
    """Base class for filter parameters – extended per module."""

    search: str | None = None
