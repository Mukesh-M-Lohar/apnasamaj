"""
ApnaSamaj – Community (Tenant) Unit Tests

Tests cover:
  • Community creation schema validation
  • Community update schema validation
  • Slug validation
"""

from __future__ import annotations

import pytest

from apps.api.modules.tenant.schemas import (
    CommunityCreateSchema,
    CommunityUpdateSchema,
    InviteMemberSchema,
)


class TestCommunitySchemas:
    """Test Pydantic schema validation for Community."""

    def test_valid_create_schema(self) -> None:
        schema = CommunityCreateSchema(
            name="My Community",
            slug="my-community",
            city="Mumbai",
            primary_language="en",
            timezone="Asia/Kolkata",
            currency="INR",
        )
        assert schema.name == "My Community"
        assert schema.slug == "my-community"
        assert schema.city == "Mumbai"
        assert schema.primary_language == "en"

    def test_slug_is_lowercased(self) -> None:
        schema = CommunityCreateSchema(name="My Community", slug="MY-COMMUNITY")
        assert schema.slug == "my-community"

    def test_invalid_slug_pattern_raises(self) -> None:
        with pytest.raises(ValueError):
            CommunityCreateSchema(name="Test", slug="invalid_slug!")

    def test_valid_update_schema(self) -> None:
        schema = CommunityUpdateSchema(name="Updated Community", city="Delhi")
        assert schema.name == "Updated Community"
        assert schema.city == "Delhi"

    def test_invite_member_schema_valid_mobile(self) -> None:
        schema = InviteMemberSchema(mobile="+91 98765 43210")
        assert schema.mobile == "+919876543210"
        assert schema.role == "member"

    def test_invite_member_schema_invalid_mobile_raises(self) -> None:
        with pytest.raises(ValueError):
            InviteMemberSchema(mobile="invalid_number")
