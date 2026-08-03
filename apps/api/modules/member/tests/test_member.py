"""
ApnaSamaj – Member Unit Tests

Tests cover:
  • Member creation schema validation
  • Mobile number formatting
"""

from __future__ import annotations

import pytest

from apps.api.modules.member.schemas import MemberCreateSchema, MemberUpdateSchema


class TestMemberSchemas:
    """Test Pydantic schema validation for Member."""

    def test_valid_member_create(self) -> None:
        schema = MemberCreateSchema(
            first_name="Rahul", last_name="Sharma", mobile="+91 98765 43210", gender="male", blood_group="O+"
        )
        assert schema.first_name == "Rahul"
        assert schema.last_name == "Sharma"
        assert schema.mobile == "+919876543210"
        assert schema.gender == "male"
        assert schema.blood_group == "O+"

    def test_invalid_mobile_raises(self) -> None:
        with pytest.raises(ValueError):
            MemberCreateSchema(first_name="Rahul", last_name="Sharma", mobile="not_a_number")

    def test_alternate_mobile_cleaned(self) -> None:
        schema = MemberCreateSchema(
            first_name="Rahul", last_name="Sharma", mobile="+919876543210", alternate_mobile="987-654-3210"
        )
        assert schema.alternate_mobile == "9876543210"

    def test_update_schema_optional_fields(self) -> None:
        schema = MemberUpdateSchema(first_name="Rohit", city="Delhi")
        assert schema.first_name == "Rohit"
        assert schema.last_name is None
        assert schema.city == "Delhi"
