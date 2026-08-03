"""
ApnaSamaj – Polling Schemas
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from apps.api.core.base_schema import BaseResponseSchema


class PollOptionCreateSchema(BaseModel):
    text: str = Field(..., max_length=255)


class PollCreateSchema(BaseModel):
    question: str = Field(..., max_length=500)
    description: str | None = None
    expires_at: datetime
    options: list[PollOptionCreateSchema] = Field(..., min_length=2, max_length=10)
    target_committee_id: UUID | None = None


class PollOptionResponse(BaseResponseSchema):
    poll_id: UUID
    text: str
    vote_count: int

    model_config = ConfigDict(from_attributes=True)


class PollResponse(BaseResponseSchema):
    question: str
    description: str | None
    expires_at: datetime
    is_active: bool
    target_committee_id: UUID | None
    options: list[PollOptionResponse]

    model_config = ConfigDict(from_attributes=True)


class PollVoteSchema(BaseModel):
    option_id: UUID
