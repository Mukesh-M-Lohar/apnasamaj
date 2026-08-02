"""
ApnaSamaj – Document Model

Centralized document storage for member photos, certificates,
identity documents, committee docs, meeting minutes, etc.
"""

from __future__ import annotations

import uuid

from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from apps.api.core.base_model import BaseModel


class Document(BaseModel):
    """A file/document uploaded to the platform."""

    __tablename__ = "documents"

    # ── Ownership ────────────────────────────────────────────────────────
    uploaded_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── Polymorphic link ─────────────────────────────────────────────────
    entity_type: Mapped[str] = mapped_column(
        String(50), nullable=False,
    )  # member, family, committee, event, complaint, etc.

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True,
    )

    # ── File Info ────────────────────────────────────────────────────────
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(100), nullable=False)  # image/jpeg, application/pdf, etc.
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)  # bytes
    file_url: Mapped[str] = mapped_column(String(512), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)  # MinIO object key

    # ── Category ─────────────────────────────────────────────────────────
    category: Mapped[str | None] = mapped_column(
        String(100), nullable=True,
    )  # photo, certificate, id_document, minutes, report

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
