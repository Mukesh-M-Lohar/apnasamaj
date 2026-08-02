"""
ApnaSamaj – Complaint Schemas

Pydantic models for request validation and response serialization.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from apps.api.core.base_schema import BaseResponse
from apps.api.modules.complaint.models import ComplaintPriority, ComplaintStatus


class ComplaintCreateSchema(BaseModel):
    title: str = Field(..., max_length=255)
    description: str
    priority: ComplaintPriority = Field(default=ComplaintPriority.MEDIUM)
    assigned_committee_id: UUID | None = None
    # reporter_id is inferred from current user context


class ComplaintUpdateSchema(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    description: str | None = None
    priority: ComplaintPriority | None = None
    status: ComplaintStatus | None = None
    assigned_committee_id: UUID | None = None
    resolution_notes: str | None = None


class ComplaintResponse(BaseResponse):
    title: str
    description: str
    status: ComplaintStatus
    priority: ComplaintPriority
    reporter_id: UUID
    assigned_committee_id: UUID | None
    resolution_notes: str | None
    
    model_config = ConfigDict(from_attributes=True)
