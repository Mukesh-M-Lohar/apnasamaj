"""
ApnaSamaj – Payment Repository

Database operations for transaction intents and webhooks.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.modules.payment.models import Transaction, TransactionStatus


class PaymentRepository:
    """Handles transaction DB operations scoped to a tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self._session = session
        self.tenant_id = tenant_id

    def _base_query(self) -> Select:
        return select(Transaction).where(
            Transaction.tenant_id == self.tenant_id,
            Transaction.is_deleted == False,  # noqa: E712
        )

    async def create_intent(self, data: dict[str, Any], created_by: UUID | None = None) -> Transaction:
        transaction = Transaction(
            tenant_id=self.tenant_id,
            created_by=created_by,
            updated_by=created_by,
            **data,
        )
        self._session.add(transaction)
        await self._session.flush()
        await self._session.refresh(transaction)
        return transaction

    async def get_by_provider_reference(self, reference: str) -> Transaction | None:
        stmt = self._base_query().where(Transaction.provider_reference == reference)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(
        self, transaction_id: UUID, status: TransactionStatus, metadata: dict | None = None
    ) -> Transaction | None:
        stmt = self._base_query().where(Transaction.id == transaction_id)
        result = await self._session.execute(stmt)
        transaction = result.scalar_one_or_none()

        if not transaction:
            return None

        transaction.status = status
        if metadata:
            transaction.provider_metadata = metadata

        await self._session.flush()
        await self._session.refresh(transaction)
        return transaction

    async def get_all_paginated(
        self,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Transaction], int]:
        stmt = self._base_query()
        count_stmt = (
            select(func.count())
            .select_from(Transaction)
            .where(
                Transaction.tenant_id == self.tenant_id,
                Transaction.is_deleted == False,  # noqa: E712
            )
        )

        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = stmt.order_by(Transaction.created_at.desc())
        stmt = stmt.offset(offset).limit(limit)

        result = await self._session.execute(stmt)
        transactions = list(result.scalars().all())

        return transactions, total
