"""
ApnaSamaj – Donation Model

Supports multiple donation types, payment modes, receipt generation,
and full audit trail for financial transparency.
"""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from apps.api.core.base_model import BaseModel


class Donation(BaseModel):
    """A financial donation/contribution to the community."""

    __tablename__ = "donations"

    # ── Who donated ──────────────────────────────────────────────────────
    member_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("members.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    family_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("families.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    donor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)  # For anonymous/external donors

    # ── Donation Details ─────────────────────────────────────────────────
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    donation_date: Mapped[date] = mapped_column(Date, nullable=False)

    purpose: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )  # general, temple, aarati, bhog, festival, construction, charity, membership, other

    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sub_category: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # ── Payment ──────────────────────────────────────────────────────────
    payment_mode: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # cash, upi, bank_transfer, cheque, card, online

    transaction_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cheque_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    bank_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ── Receipt ──────────────────────────────────────────────────────────
    receipt_number: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    receipt_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # ── Status ───────────────────────────────────────────────────────────
    status: Mapped[str] = mapped_column(String(20), default="completed", nullable=False)
    # completed, pending, cancelled, refunded

    # ── Remarks ──────────────────────────────────────────────────────────
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Event link (optional) ────────────────────────────────────────────
    event_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("events.id", ondelete="SET NULL"),
        nullable=True,
    )
