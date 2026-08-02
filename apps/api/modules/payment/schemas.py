"""
ApnaSamaj – Payment Schemas
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from apps.api.core.base_schema import BaseResponse
from apps.api.modules.payment.models import EntityType, PaymentProvider, TransactionStatus


class TransactionIntentSchema(BaseModel):
    amount: Decimal
    currency: str = "INR"
    provider: PaymentProvider = PaymentProvider.RAZORPAY
    related_entity_type: EntityType
    related_entity_id: UUID


class WebhookPayloadSchema(BaseModel):
    """Generic representation of what a webhook sends us."""
    provider_reference: str
    status: TransactionStatus
    metadata: dict[str, Any] | None = None


class TransactionResponse(BaseResponse):
    amount: Decimal
    currency: str
    status: TransactionStatus
    provider: PaymentProvider
    provider_reference: str | None
    related_entity_type: EntityType
    related_entity_id: UUID
    payer_id: UUID
    
    model_config = ConfigDict(from_attributes=True)
