"""
ApnaSamaj – Facility Schemas

Pydantic models for request validation and response serialization.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator

from apps.api.core.base_schema import BaseResponse
from apps.api.modules.facility.models import BookingStatus


class FacilityCreateSchema(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = None
    capacity: int = 0
    hourly_rate: Decimal | None = None
    is_active: bool = True


class FacilityUpdateSchema(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    capacity: int | None = None
    hourly_rate: Decimal | None = None
    is_active: bool | None = None


class FacilityResponse(BaseResponse):
    name: str
    description: str | None
    capacity: int
    hourly_rate: Decimal | None
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)


class FacilityBookingCreateSchema(BaseModel):
    start_time: datetime
    end_time: datetime
    
    @field_validator("end_time")
    def validate_time_range(cls, v: datetime, info: Any) -> datetime:
        if "start_time" in info.data and v <= info.data["start_time"]:
            raise ValueError("end_time must be after start_time")
        return v


class FacilityBookingUpdateSchema(BaseModel):
    status: BookingStatus | None = None
    total_cost: Decimal | None = None


class FacilityBookingResponse(BaseResponse):
    facility_id: UUID
    booked_by_id: UUID
    start_time: datetime
    end_time: datetime
    status: BookingStatus
    total_cost: Decimal | None
    
    model_config = ConfigDict(from_attributes=True)
