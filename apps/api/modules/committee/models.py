"""
ApnaSamaj – Committee Models

Committee management with term tracking and member roles.
"""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from apps.api.core.base_model import BaseModel


class Committee(BaseModel):
    """A governing committee within a community (e.g. Executive Board 2024-2026)."""

    __tablename__ = "committees"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    term_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    term_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)  # active, past, upcoming


class CommitteeMember(BaseModel):
    """A member's role within a specific committee."""

    __tablename__ = "committee_members"

    committee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("committees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    member_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("members.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    position: Mapped[str] = mapped_column(String(100), nullable=False)
    # president, chairman, secretary, treasurer, executive_member, etc.

    responsibilities: Mapped[str | None] = mapped_column(Text, nullable=True)
    joined_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    left_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
