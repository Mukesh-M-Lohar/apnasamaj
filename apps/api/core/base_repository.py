"""
ApnaSamaj – Generic Async Repository

Implements the Repository Pattern with full CRUD, soft-delete, pagination,
sorting, and filtering over any SQLAlchemy model that extends BaseModel.

Design decisions:
  • All queries are tenant-scoped by default (WHERE tenant_id = ?).
  • Soft-deleted rows are excluded unless explicitly requested.
  • Uses SQLAlchemy 2.0 select() style (no legacy Query API).
  • Returns ORM instances – schema conversion happens in the service layer.
"""

from __future__ import annotations

import math
from datetime import UTC, datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.base_model import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


class BaseRepository(Generic[ModelT]):
    """Generic async repository for tenant-scoped CRUD operations."""

    def __init__(self, model: type[ModelT], session: AsyncSession) -> None:
        self._model = model
        self._session = session

    # ── Helpers ──────────────────────────────────────────────────────────

    def _base_query(self, tenant_id: UUID, include_deleted: bool = False) -> Select:
        """Build a base SELECT filtered by tenant and soft-delete."""
        stmt = select(self._model).where(self._model.tenant_id == tenant_id)
        if not include_deleted:
            stmt = stmt.where(self._model.is_deleted == False)  # noqa: E712
        return stmt

    # ── Create ───────────────────────────────────────────────────────────

    async def create(self, tenant_id: UUID, data: dict[str, Any], created_by: UUID | None = None) -> ModelT:
        """Insert a new row."""
        instance = self._model(
            tenant_id=tenant_id,
            created_by=created_by,
            updated_by=created_by,
            **data,
        )
        self._session.add(instance)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    # ── Read ─────────────────────────────────────────────────────────────

    async def get_by_id(
        self,
        tenant_id: UUID,
        record_id: UUID,
        include_deleted: bool = False,
    ) -> ModelT | None:
        """Fetch a single record by primary key."""
        stmt = self._base_query(tenant_id, include_deleted).where(self._model.id == record_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        tenant_id: UUID,
        offset: int = 0,
        limit: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        include_deleted: bool = False,
    ) -> list[ModelT]:
        """List records with pagination and sorting."""
        stmt = self._base_query(tenant_id, include_deleted)

        # Dynamic sorting
        sort_column = getattr(self._model, sort_by, self._model.created_at)
        if sort_order == "desc":
            stmt = stmt.order_by(sort_column.desc())
        else:
            stmt = stmt.order_by(sort_column.asc())

        stmt = stmt.offset(offset).limit(limit)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count(self, tenant_id: UUID, include_deleted: bool = False) -> int:
        """Count total records for pagination metadata."""
        stmt = select(func.count()).select_from(self._model).where(self._model.tenant_id == tenant_id)
        if not include_deleted:
            stmt = stmt.where(self._model.is_deleted == False)  # noqa: E712
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_paginated(
        self,
        tenant_id: UUID,
        page: int = 1,
        per_page: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> dict[str, Any]:
        """Return paginated results with metadata."""
        total = await self.count(tenant_id)
        total_pages = math.ceil(total / per_page) if per_page > 0 else 0
        offset = (page - 1) * per_page
        items = await self.get_all(tenant_id, offset=offset, limit=per_page, sort_by=sort_by, sort_order=sort_order)
        return {
            "items": items,
            "meta": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            },
        }

    # ── Update ───────────────────────────────────────────────────────────

    async def update(
        self,
        tenant_id: UUID,
        record_id: UUID,
        data: dict[str, Any],
        updated_by: UUID | None = None,
    ) -> ModelT | None:
        """Partial update of an existing record."""
        instance = await self.get_by_id(tenant_id, record_id)
        if not instance:
            return None
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        if updated_by:
            instance.updated_by = updated_by
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    # ── Soft Delete ──────────────────────────────────────────────────────

    async def soft_delete(
        self,
        tenant_id: UUID,
        record_id: UUID,
        deleted_by: UUID | None = None,
    ) -> bool:
        """Mark a record as deleted (soft delete)."""
        instance = await self.get_by_id(tenant_id, record_id)
        if not instance:
            return False
        instance.is_deleted = True
        instance.deleted_at = datetime.now(UTC)
        if deleted_by:
            instance.updated_by = deleted_by
        await self._session.flush()
        return True

    async def restore(self, tenant_id: UUID, record_id: UUID) -> ModelT | None:
        """Restore a soft-deleted record."""
        instance = await self.get_by_id(tenant_id, record_id, include_deleted=True)
        if not instance or not instance.is_deleted:
            return None
        instance.is_deleted = False
        instance.deleted_at = None
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    # ── Hard Delete (admin only) ─────────────────────────────────────────

    async def hard_delete(self, tenant_id: UUID, record_id: UUID) -> bool:
        """Permanently delete a record – use with caution."""
        instance = await self.get_by_id(tenant_id, record_id, include_deleted=True)
        if not instance:
            return False
        await self._session.delete(instance)
        await self._session.flush()
        return True

    # ── Existence Checks ─────────────────────────────────────────────────

    async def exists(self, tenant_id: UUID, record_id: UUID) -> bool:
        """Check if a record exists."""
        stmt = (
            select(func.count())
            .select_from(self._model)
            .where(
                self._model.tenant_id == tenant_id,
                self._model.id == record_id,
                self._model.is_deleted == False,  # noqa: E712
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one() > 0

    async def find_by(self, tenant_id: UUID, **kwargs: Any) -> list[ModelT]:
        """Find records matching arbitrary column filters."""
        stmt = self._base_query(tenant_id)
        for key, value in kwargs.items():
            if hasattr(self._model, key):
                stmt = stmt.where(getattr(self._model, key) == value)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_one_by(self, tenant_id: UUID, **kwargs: Any) -> ModelT | None:
        """Find a single record matching filters."""
        stmt = self._base_query(tenant_id)
        for key, value in kwargs.items():
            if hasattr(self._model, key):
                stmt = stmt.where(getattr(self._model, key) == value)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
