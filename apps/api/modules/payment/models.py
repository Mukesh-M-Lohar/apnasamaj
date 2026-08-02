"""
ApnaSamaj – Payment Models

Vendor-agnostic transaction engine for Stripe/Razorpay integrations.
"""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, String, Text
from sqlalchemy import Column, Numeric
from sqlalchemy.dialects.postgresql import JSONB

from apps.api.core.models.base import BaseModel

if TYPE_CHECKING:
    from apps.api.modules.member.models import Member


class PaymentProvider(str, enum.Enum):
    STRIPE = "stripe"
    RAZORPAY = "razorpay"
    MANUAL = "manual"


class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"


class EntityType(str, enum.Enum):
    DONATION = "donation"
    FACILITY_BOOKING = "facility_booking"


class Transaction(BaseModel, table=True):
    """A financial transaction tied to an entity."""
    __tablename__ = "transactions"

    amount: float = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    currency: str = Field(default="INR", max_length=3)
    
    status: TransactionStatus = Field(default=TransactionStatus.PENDING)
    provider: PaymentProvider = Field(default=PaymentProvider.RAZORPAY)
    
    # Stripe PaymentIntent ID or Razorpay Order ID
    provider_reference: str | None = Field(default=None, sa_column=Column(String(255), unique=True))
    
    # What is this payment for?
    related_entity_type: EntityType = Field(nullable=False)
    related_entity_id: UUID = Field(nullable=False)
    
    # Who paid it
    payer_id: UUID = Field(foreign_key="members.id", nullable=False)
    
    # Dump full webhook payload for audit
    provider_metadata: dict | None = Field(default=None, sa_column=Column(JSONB))

    # Relationships
    payer: "Member" = Relationship()
