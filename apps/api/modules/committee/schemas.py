"""
ApnaSamaj – Committee Pydantic Schemas

Request/response models for committees and their members.
"""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import Field, field_validator

from apps.api.core.base_schema import BaseSchema
from apps.api.modules.member.schemas import MemberListResponse


# ── Committee ────────────────────────────────────────────────────────────

class CommitteeCreateSchema(BaseSchema):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    term_start: date | None = None
    term_end: date | None = None
    status: str = Field(default="active", max_length=20)

    @field_validator("term_end")
    @classmethod
    def validate_term_dates(cls, term_end: date | None, info) -> date | None:
        if term_end and "term_start" in info.data:
            term_start = info.data["term_start"]
            if term_start and term_end < term_start:
                raise ValueError("term_end cannot be before term_start")
        return term_end


class CommitteeUpdateSchema(BaseSchema):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    term_start: date | None = None
    term_end: date | None = None
    status: str | None = Field(default=None, max_length=20)

    @field_validator("term_end")
    @classmethod
    def validate_term_dates(cls, term_end: date | None, info) -> date | None:
        if term_end and "term_start" in info.data:
            term_start = info.data["term_start"]
            if term_start and term_end < term_start:
                raise ValueError("term_end cannot be before term_start")
        return term_end


# ── Committee Members ────────────────────────────────────────────────────

class AddCommitteeMemberSchema(BaseSchema):
    member_id: UUID
    position: str = Field(..., max_length=100)
    responsibilities: str | None = None
    joined_date: date | None = None
    left_date: date | None = None
    status: str = Field(default="active", max_length=20)


class CommitteeMemberResponse(BaseSchema):
    id: UUID
    committee_id: UUID
    member_id: UUID
    position: str
    responsibilities: str | None = None
    joined_date: date | None = None
    left_date: date | None = None
    status: str
    
    member: MemberListResponse


class CommitteeResponse(BaseSchema):
    id: UUID
    name: str
    description: str | None = None
    term_start: date | None = None
    term_end: date | None = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    members: list[CommitteeMemberResponse] = Field(default_factory=list)
