"""
ApnaSamaj – Member Model

Stores all member profile data within a community.
Each member belongs to exactly one tenant and optionally one family.
"""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from apps.api.core.base_model import BaseModel


class Member(BaseModel):
    """Community member profile."""

    __tablename__ = "members"

    # ── Link to User (optional – not all members have app accounts) ─────
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ── Link to Family ──────────────────────────────────────────────────
    family_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("families.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ── Personal Info ────────────────────────────────────────────────────
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    photo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)  # male, female, other
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    anniversary_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # ── Professional ─────────────────────────────────────────────────────
    occupation: Mapped[str | None] = mapped_column(String(255), nullable=True)
    education: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ── Medical ──────────────────────────────────────────────────────────
    blood_group: Mapped[str | None] = mapped_column(String(5), nullable=True)

    # ── Contact ──────────────────────────────────────────────────────────
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mobile: Mapped[str | None] = mapped_column(String(15), nullable=True, index=True)
    alternate_mobile: Mapped[str | None] = mapped_column(String(15), nullable=True)

    # ── Address ──────────────────────────────────────────────────────────
    address_line1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_line2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True, default="India")
    pincode: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # ── Emergency Contact ────────────────────────────────────────────────
    emergency_contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    emergency_contact_mobile: Mapped[str | None] = mapped_column(String(15), nullable=True)
    emergency_contact_relation: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # ── Status ───────────────────────────────────────────────────────────
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False,
    )  # active, inactive, deceased, migrated

    # ── Membership ───────────────────────────────────────────────────────
    membership_number: Mapped[str | None] = mapped_column(String(50), nullable=True, unique=True)
    membership_expiry: Mapped[date | None] = mapped_column(Date, nullable=True)

    # ── Extra ────────────────────────────────────────────────────────────
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
