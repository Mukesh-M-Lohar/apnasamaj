"""
ApnaSamaj – Tenant (Community) Model

The Tenant table represents a community / organization.
This is the root entity for multi-tenant isolation.
Uses GlobalBaseModel because it does NOT have a tenant_id itself.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.api.core.base_model import GlobalBaseModel


class Tenant(GlobalBaseModel):
    """
    A community / organization that uses the platform.

    All other tenant-scoped tables reference this via tenant_id FK.
    """

    __tablename__ = "tenants"

    # ── Identity ─────────────────────────────────────────────────────────
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # ── Contact ──────────────────────────────────────────────────────────
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    website: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # ── Address ──────────────────────────────────────────────────────────
    address_line1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_line2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True, default="India")
    pincode: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # ── Localization ─────────────────────────────────────────────────────
    primary_language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    secondary_language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Kolkata", nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)

    # ── Social / Config ──────────────────────────────────────────────────
    social_links: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    settings: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # ── Status ───────────────────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"), nullable=False)

    # ── Relationships (lazy loaded) ──────────────────────────────────────
    # Defined via back_populates in child models
