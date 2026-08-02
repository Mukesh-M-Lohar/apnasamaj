"""
ApnaSamaj – Complaint Model

Community grievance/complaint tracking with priority, assignment,
status workflow, and attachments.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from apps.api.core.base_model import BaseModel


class Complaint(BaseModel):
    """A complaint or grievance raised by a community member."""

    __tablename__ = "complaints"

    complaint_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)

    # ── Who raised it ────────────────────────────────────────────────────
    raised_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("members.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Details ──────────────────────────────────────────────────────────
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)  # maintenance, financial, social, other
    priority: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)  # low, medium, high, critical

    # ── Assignment ───────────────────────────────────────────────────────
    assigned_to_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("members.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── Status ───────────────────────────────────────────────────────────
    status: Mapped[str] = mapped_column(
        String(20), default="open", nullable=False,
    )  # open, in_progress, resolved, closed, rejected

    # ── Resolution ───────────────────────────────────────────────────────
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # ── Attachments ──────────────────────────────────────────────────────
    attachments: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # list of file URLs
