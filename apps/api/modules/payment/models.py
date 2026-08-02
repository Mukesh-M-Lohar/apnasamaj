"""
ApnaSamaj – Payment Models

Vendor-agnostic transaction engine for Stripe/Razorpay integrations.
"""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from apps.api.core.base_model import BaseModel

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


class Transaction(BaseModel):
    """A financial transaction tied to an entity."""

    __tablename__ = "transactions"

    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR")

    status: Mapped[TransactionStatus] = mapped_column(default=TransactionStatus.PENDING)
    provider: Mapped[PaymentProvider] = mapped_column(default=PaymentProvider.RAZORPAY)

    # Stripe PaymentIntent ID or Razorpay Order ID
    provider_reference: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True
    )

    # What is this payment for?
    related_entity_type: Mapped[EntityType] = mapped_column(nullable=False)
    related_entity_id: Mapped[UUID] = mapped_column(nullable=False)

    # Who paid it
    payer_id: Mapped[UUID] = mapped_column(ForeignKey("members.id"), nullable=False)

    # Dump full webhook payload for audit
    provider_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    payer: Mapped["Member"] = relationship()
