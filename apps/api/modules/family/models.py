"""
ApnaSamaj – Family Models

Family management with multi-generation support and relationship mapping.

Design decisions:
  • Family is the container; FamilyMember is the M2M with relationship type.
  • family_head_id points to the designated head member.
  • Relationship types cover parent/child/spouse/sibling and custom.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from apps.api.core.base_model import BaseModel


class Family(BaseModel):
    """A family unit within a community."""

    __tablename__ = "families"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    family_code: Mapped[str | None] = mapped_column(String(50), nullable=True, unique=True)

    family_head_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("members.id", ondelete="SET NULL"),
        nullable=True,
    )

    address_line1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_line2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True, default="India")
    pincode: Mapped[str | None] = mapped_column(String(10), nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class FamilyMember(BaseModel):
    """
    Maps a member to a family with a relationship type.
    Enables multi-generation family tree rendering.
    """

    __tablename__ = "family_members"

    family_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("families.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    member_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("members.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationship to family head or another member
    related_to_member_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("members.id", ondelete="SET NULL"),
        nullable=True,
    )

    relationship_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )  # head, spouse, son, daughter, father, mother, sibling, other

    generation: Mapped[int | None] = mapped_column(nullable=True)  # 0 = head gen, 1 = child, -1 = parent
