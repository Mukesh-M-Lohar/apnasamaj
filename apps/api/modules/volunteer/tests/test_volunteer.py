"""
ApnaSamaj – Volunteer Unit Tests

Tests cover:
  • Volunteer schema validation (rating, hours constraints)
"""

from __future__ import annotations

import pytest
from decimal import Decimal
from uuid import uuid4

from apps.api.modules.volunteer.schemas import VolunteerUpdateSchema, VolunteerAssignmentUpdateSchema

class TestVolunteerSchemas:
    """Test Pydantic schema validation for Volunteer."""

    def test_valid_volunteer_update(self) -> None:
        schema = VolunteerUpdateSchema(
            skills=["usher", "first-aid"],
            rating=Decimal("4.5")
        )
        assert "usher" in schema.skills
        assert schema.rating == Decimal("4.5")

    def test_invalid_rating_raises(self) -> None:
        with pytest.raises(ValueError):
            VolunteerUpdateSchema(
                rating=Decimal("5.5")  # Rating is capped at 5
            )

    def test_invalid_hours_raises(self) -> None:
        with pytest.raises(ValueError):
            VolunteerAssignmentUpdateSchema(
                hours=Decimal("-2.5")  # Hours cannot be negative
            )
