"""
ApnaSamaj – Donation Unit Tests

Tests cover:
  • Donation schema validation (amount > 0, donor present)
"""

from __future__ import annotations

import pytest
from datetime import date
from decimal import Decimal
from uuid import uuid4

from apps.api.modules.donation.schemas import DonationCreateSchema

class TestDonationSchemas:
    """Test Pydantic schema validation for Donation."""

    def test_valid_donation_create(self) -> None:
        schema = DonationCreateSchema(
            member_id=uuid4(),
            amount=Decimal("1500.50"),
            donation_date=date(2024, 1, 15),
            purpose="Temple Construction",
            payment_mode="upi"
        )
        assert schema.amount == Decimal("1500.50")
        assert schema.purpose == "Temple Construction"

    def test_invalid_amount_raises(self) -> None:
        with pytest.raises(ValueError):
            DonationCreateSchema(
                donor_name="Anonymous",
                amount=Decimal("-500.00"),  # negative amount
                donation_date=date(2024, 1, 15),
                purpose="Charity",
                payment_mode="cash"
            )

    def test_missing_donor_raises(self) -> None:
        with pytest.raises(ValueError):
            DonationCreateSchema(
                # Missing member_id, family_id, or donor_name
                amount=Decimal("100.00"),
                donation_date=date(2024, 1, 15),
                purpose="Charity",
                payment_mode="cash"
            )
