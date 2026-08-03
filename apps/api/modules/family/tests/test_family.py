"""
ApnaSamaj – Family Unit Tests

Tests cover:
  • Family creation schema validation
  • AddFamilyMemberSchema validation
"""

from __future__ import annotations

from uuid import uuid4

from apps.api.modules.family.schemas import (
    AddFamilyMemberSchema,
    FamilyCreateSchema,
)


class TestFamilySchemas:
    """Test Pydantic schema validation for Family."""

    def test_valid_family_create(self) -> None:
        schema = FamilyCreateSchema(name="Sharma Family", city="Delhi")
        assert schema.name == "Sharma Family"
        assert schema.city == "Delhi"

    def test_add_family_member_schema(self) -> None:
        member_id = uuid4()
        head_id = uuid4()
        schema = AddFamilyMemberSchema(
            member_id=member_id, related_to_member_id=head_id, relationship_type="spouse", generation=0
        )
        assert schema.member_id == member_id
        assert schema.relationship_type == "spouse"
        assert schema.generation == 0

    def test_add_family_member_without_generation(self) -> None:
        member_id = uuid4()
        schema = AddFamilyMemberSchema(member_id=member_id, relationship_type="child")
        assert schema.member_id == member_id
        assert schema.relationship_type == "child"
        assert schema.generation is None  # Should be computed by service
