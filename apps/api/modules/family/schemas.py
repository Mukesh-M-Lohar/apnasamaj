"""
ApnaSamaj – Family Pydantic Schemas

Request/response models for families and family members.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import Field

from apps.api.core.base_schema import BaseSchema
from apps.api.modules.member.schemas import MemberResponse


# ── Create / Update Family ───────────────────────────────────────────────

class FamilyCreateSchema(BaseSchema):
    """POST /families – create a new family unit."""

    name: str = Field(..., min_length=1, max_length=255)
    family_code: str | None = Field(default=None, max_length=50)
    family_head_id: UUID | None = None

    address_line1: str | None = Field(default=None, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default="India", max_length=100)
    pincode: str | None = Field(default=None, max_length=10)
    notes: str | None = None


class FamilyUpdateSchema(BaseSchema):
    """PATCH /families/{id} – update family details."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    family_code: str | None = Field(default=None, max_length=50)
    family_head_id: UUID | None = None

    address_line1: str | None = Field(default=None, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
    pincode: str | None = Field(default=None, max_length=10)
    notes: str | None = None


# ── Family Members ───────────────────────────────────────────────────────

class AddFamilyMemberSchema(BaseSchema):
    """POST /families/{id}/members – link a member to the family."""

    member_id: UUID
    related_to_member_id: UUID | None = Field(
        default=None,
        description="ID of the member they are related to (usually the head)."
    )
    relationship_type: str = Field(..., max_length=50, description="spouse, child, parent, sibling, etc.")
    generation: int | None = Field(
        default=None,
        description="Generation relative to head (0=head, 1=child, -1=parent). Computed automatically if not provided."
    )


class FamilyMemberResponse(BaseSchema):
    """Represents a member within a family (junction table info)."""

    id: UUID
    family_id: UUID
    member_id: UUID
    related_to_member_id: UUID | None = None
    relationship_type: str
    generation: int | None = None
    member: MemberResponse  # Embedded full profile


class FamilyResponse(BaseSchema):
    """Family detail response with a flat list of members."""

    id: UUID
    name: str
    family_code: str | None = None
    family_head_id: UUID | None = None
    
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    pincode: str | None = None
    notes: str | None = None

    created_at: datetime
    updated_at: datetime
    
    members: list[FamilyMemberResponse] = Field(default_factory=list)


# ── Structured Tree ──────────────────────────────────────────────────────

class FamilyTreeNode(BaseSchema):
    """A node in the hierarchical family tree."""

    member: MemberResponse
    relationship_type: str
    generation: int | None = None
    children: list["FamilyTreeNode"] = Field(default_factory=list)

class FamilyTreeResponse(BaseSchema):
    """Hierarchical view of the family starting from the head."""

    family: FamilyResponse
    tree: FamilyTreeNode | None = None
