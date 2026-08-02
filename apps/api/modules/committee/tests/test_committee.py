"""
ApnaSamaj – Committee Unit Tests

Tests cover:
  • Committee creation schema validation (term dates validation)
"""

from __future__ import annotations

import pytest
from datetime import date

from apps.api.modules.committee.schemas import CommitteeCreateSchema

class TestCommitteeSchemas:
    """Test Pydantic schema validation for Committee."""

    def test_valid_committee_create(self) -> None:
        schema = CommitteeCreateSchema(
            name="Executive Board 2024",
            term_start=date(2024, 1, 1),
            term_end=date(2025, 12, 31)
        )
        assert schema.name == "Executive Board 2024"
        assert schema.term_start == date(2024, 1, 1)

    def test_invalid_term_dates_raises(self) -> None:
        with pytest.raises(ValueError):
            CommitteeCreateSchema(
                name="Executive Board 2024",
                term_start=date(2024, 1, 1),
                term_end=date(2023, 12, 31)  # end before start
            )
