"""
ApnaSamaj – Event Unit Tests

Tests cover:
  • Event schema validation (dates and required fields)
"""

from __future__ import annotations

import pytest
from datetime import date

from apps.api.modules.event.schemas import EventCreateSchema

class TestEventSchemas:
    """Test Pydantic schema validation for Event."""

    def test_valid_event_create(self) -> None:
        schema = EventCreateSchema(
            title="Diwali Mela 2024",
            event_type="festival",
            start_date=date(2024, 11, 1),
            end_date=date(2024, 11, 3)
        )
        assert schema.title == "Diwali Mela 2024"
        assert schema.start_date == date(2024, 11, 1)

    def test_invalid_dates_raises(self) -> None:
        with pytest.raises(ValueError):
            EventCreateSchema(
                title="Diwali Mela 2024",
                event_type="festival",
                start_date=date(2024, 11, 5),
                end_date=date(2024, 11, 3)  # end before start
            )
