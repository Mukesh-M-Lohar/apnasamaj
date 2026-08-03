"""
ApnaSamaj – Payment Service

Business logic for generic intent generation and webhooks processing.
"""

from __future__ import annotations

import logging
import math
import uuid
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.exceptions import NotFoundException
from apps.api.modules.payment.repository import PaymentRepository
from apps.api.modules.payment.schemas import (
    TransactionIntentSchema,
    TransactionResponse,
    WebhookPayloadSchema,
)

logger = logging.getLogger(__name__)


class PaymentService:
    """Business logic for intent generation and transaction state management."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self._repo = PaymentRepository(session, tenant_id)
        self.tenant_id = tenant_id

    async def create_intent(
        self,
        data: TransactionIntentSchema,
        payer_id: UUID,
    ) -> TransactionResponse:
        """
        Creates an intent. In a real environment, this would call Stripe SDK
        or Razorpay SDK to generate a client_secret or order_id.
        """
        payload = data.model_dump(exclude_none=True)
        payload["payer_id"] = payer_id

        # Simulate Provider reference generation
        payload["provider_reference"] = f"pi_{uuid.uuid4().hex[:14]}"

        transaction = await self._repo.create_intent(
            data=payload,
            created_by=payer_id,
        )
        logger.info("Payment intent created for member %s (Ref: %s)", payer_id, transaction.provider_reference)
        return TransactionResponse.model_validate(transaction)

    async def handle_webhook(self, payload: WebhookPayloadSchema) -> dict:
        """
        Process incoming webhooks from the payment gateway.
        """
        transaction = await self._repo.get_by_provider_reference(payload.provider_reference)
        if not transaction:
            logger.warning("Received webhook for unknown transaction: %s", payload.provider_reference)
            raise NotFoundException("Transaction", payload.provider_reference)

        await self._repo.update_status(transaction_id=transaction.id, status=payload.status, metadata=payload.metadata)

        # Note: In a full event-driven system, this is where we would emit an event
        # (e.g., "TRANSACTION_SUCCEEDED") that the Donation or Facility module
        # listens to in order to update their own tables.
        # For now, the transaction state itself is updated securely.

        logger.info("Webhook processed for transaction %s. New status: %s", transaction.id, payload.status)
        return {"status": "success", "transaction_id": str(transaction.id)}

    async def list_transactions(
        self,
        page: int = 1,
        per_page: int = 20,
    ) -> dict[str, Any]:
        offset = (page - 1) * per_page
        transactions, total = await self._repo.get_all_paginated(offset=offset, limit=per_page)

        total_pages = math.ceil(total / per_page) if per_page > 0 else 0
        items = [TransactionResponse.model_validate(t) for t in transactions]

        return {
            "items": items,
            "meta": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            },
        }
