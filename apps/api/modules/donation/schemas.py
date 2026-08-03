"""
ApnaSamaj – Donation Pydantic Schemas

Request/response models for financial donations and summary rollups.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import Field, field_validator

from apps.api.core.base_schema import BaseSchema

# ── Donation ─────────────────────────────────────────────────────────────


class DonationCreateSchema(BaseSchema):
    member_id: UUID | None = None
    family_id: UUID | None = None
    donor_name: str | None = Field(default=None, max_length=255)

    amount: Decimal = Field(..., gt=0, decimal_places=2)
    currency: str = Field(default="INR", max_length=3)
    donation_date: date

    purpose: str = Field(..., max_length=100)
    category: str | None = Field(default=None, max_length=100)
    sub_category: str | None = Field(default=None, max_length=100)

    payment_mode: str = Field(..., max_length=50)
    transaction_reference: str | None = Field(default=None, max_length=255)
    cheque_number: str | None = Field(default=None, max_length=50)
    bank_name: str | None = Field(default=None, max_length=255)

    status: str = Field(default="completed", max_length=20)
    remarks: str | None = None
    event_id: UUID | None = None

    @field_validator("donor_name")
    @classmethod
    def validate_donor(cls, donor_name: str | None, info) -> str | None:
        member_id = info.data.get("member_id")
        family_id = info.data.get("family_id")
        if not member_id and not family_id and not donor_name:
            raise ValueError("Must provide either member_id, family_id, or donor_name")
        return donor_name


class DonationUpdateSchema(BaseSchema):
    donor_name: str | None = Field(default=None, max_length=255)
    amount: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    donation_date: date | None = None
    purpose: str | None = Field(default=None, max_length=100)
    payment_mode: str | None = Field(default=None, max_length=50)
    transaction_reference: str | None = Field(default=None, max_length=255)
    status: str | None = Field(default=None, max_length=20)
    remarks: str | None = None


class DonationResponse(BaseSchema):
    id: UUID
    member_id: UUID | None = None
    family_id: UUID | None = None
    donor_name: str | None = None

    amount: Decimal
    currency: str
    donation_date: date
    purpose: str
    category: str | None = None
    sub_category: str | None = None

    payment_mode: str
    transaction_reference: str | None = None
    cheque_number: str | None = None
    bank_name: str | None = None

    receipt_number: str | None = None
    receipt_url: str | None = None

    status: str
    remarks: str | None = None
    event_id: UUID | None = None

    created_at: datetime
    updated_at: datetime


# ── Summary/Rollups ──────────────────────────────────────────────────────


class DonationSummaryItem(BaseSchema):
    group_key: str
    total_amount: Decimal
    count: int


class DonationSummaryResponse(BaseSchema):
    total_donations: Decimal
    total_count: int
    by_purpose: list[DonationSummaryItem]
    by_payment_mode: list[DonationSummaryItem]
