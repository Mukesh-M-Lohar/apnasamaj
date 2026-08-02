"""
ApnaSamaj – Payment API Routes

Endpoints for generating intents and receiving provider webhooks.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.base_schema import ApiResponse, PaginatedResponse
from apps.api.core.database import get_db
from apps.api.core.dependencies import get_current_tenant_id, get_current_user_id
from apps.api.core.permissions import Permission, RequirePermissions
from apps.api.modules.payment.schemas import (
    TransactionIntentSchema,
    TransactionResponse,
    WebhookPayloadSchema,
)
from apps.api.modules.payment.service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post(
    "/intent",
    response_model=ApiResponse[TransactionResponse],
    summary="Create Payment Intent",
    description="Initiates a secure transaction for frontend checkout.",
)
async def create_intent(
    body: TransactionIntentSchema,
    tenant_id: UUID = Depends(get_current_tenant_id),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TransactionResponse]:
    service = PaymentService(db, tenant_id)
    result = await service.create_intent(body, payer_id=user_id)
    return ApiResponse(data=result)


@router.post(
    "/webhook",
    response_model=ApiResponse[dict],
    summary="Payment Provider Webhook",
    description="Endpoint for Stripe/Razorpay to send asynchronous status updates.",
)
async def payment_webhook(
    body: WebhookPayloadSchema,
    # In a real environment, we'd verify the signature here instead of tenant_id
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    service = PaymentService(db, tenant_id)
    result = await service.handle_webhook(body)
    return ApiResponse(data=result)


@router.get(
    "",
    response_model=PaginatedResponse[TransactionResponse],
    summary="List Transactions",
    dependencies=[Depends(RequirePermissions(Permission.DONATION_READ))],
)
async def list_transactions(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[TransactionResponse]:
    service = PaymentService(db, tenant_id)
    result = await service.list_transactions(page=page, per_page=per_page)
    return PaginatedResponse(data=result["items"], meta=result["meta"])
