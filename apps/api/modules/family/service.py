"""
ApnaSamaj – Family Service

Business logic for family management.
Includes logic for building multi-generation family trees.
"""

from __future__ import annotations

import logging
import math
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.exceptions import (
    AppException,
    NotFoundException,
)
from apps.api.modules.family.repository import FamilyRepository
from apps.api.modules.family.schemas import (
    AddFamilyMemberSchema,
    FamilyCreateSchema,
    FamilyMemberResponse,
    FamilyResponse,
    FamilyTreeNode,
    FamilyTreeResponse,
    FamilyUpdateSchema,
)
from apps.api.modules.member.schemas import MemberResponse

logger = logging.getLogger(__name__)


class FamilyService:
    """Business logic for family management."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self._repo = FamilyRepository(session, tenant_id)

    # ── Create ───────────────────────────────────────────────────────────

    async def create_family(
        self,
        data: FamilyCreateSchema,
        created_by: UUID | None = None,
    ) -> FamilyResponse:
        """Create a new family."""
        family = await self._repo.create(
            data=data.model_dump(exclude_none=True),
            created_by=created_by,
        )
        logger.info("Family created: %s", family.name)

        # If head is provided, add them as head
        if data.family_head_id:
            await self.add_member(
                family.id,
                AddFamilyMemberSchema(member_id=data.family_head_id, relationship_type="head", generation=0),
                created_by=created_by,
            )

        return await self.get_family(family.id)

    # ── Read ─────────────────────────────────────────────────────────────

    async def get_family(self, family_id: UUID) -> FamilyResponse:
        """Get a family and its members (flat list)."""
        family = await self._repo.get_by_id(family_id)
        if not family:
            raise NotFoundException("Family", str(family_id))

        members_data = await self._repo.get_family_members(family_id)

        # Map to response schema
        members = []
        for fm in members_data:
            member_resp = MemberResponse.model_validate(fm.member_obj)
            members.append(
                FamilyMemberResponse(
                    id=fm.id,
                    family_id=fm.family_id,
                    member_id=fm.member_id,
                    related_to_member_id=fm.related_to_member_id,
                    relationship_type=fm.relationship_type,
                    generation=fm.generation,
                    member=member_resp,
                )
            )

        response = FamilyResponse.model_validate(family)
        response.members = members
        return response

    async def list_families(
        self,
        page: int = 1,
        per_page: int = 20,
        search: str | None = None,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> dict[str, Any]:
        """List families with pagination and search."""
        offset = (page - 1) * per_page

        families, total = await self._repo.get_all_paginated(
            offset=offset,
            limit=per_page,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        total_pages = math.ceil(total / per_page) if per_page > 0 else 0

        items = [FamilyResponse.model_validate(f) for f in families]

        return {
            "items": items,
            "meta": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            },
        }

    # ── Update ───────────────────────────────────────────────────────────

    async def update_family(
        self,
        family_id: UUID,
        data: FamilyUpdateSchema,
        updated_by: UUID | None = None,
    ) -> FamilyResponse:
        """Update a family."""
        family = await self._repo.update(
            family_id=family_id,
            data=data.model_dump(exclude_unset=True),
            updated_by=updated_by,
        )
        if not family:
            raise NotFoundException("Family", str(family_id))

        return await self.get_family(family_id)

    # ── Delete ───────────────────────────────────────────────────────────

    async def delete_family(self, family_id: UUID, deleted_by: UUID | None = None) -> dict:
        """Soft-delete a family."""
        success = await self._repo.soft_delete(family_id, deleted_by)
        if not success:
            raise NotFoundException("Family", str(family_id))
        logger.info("Family soft-deleted: %s by %s", family_id, deleted_by)
        return {"message": "Family deleted successfully"}

    # ── Members (Junction) ───────────────────────────────────────────────

    async def add_member(
        self,
        family_id: UUID,
        data: AddFamilyMemberSchema,
        created_by: UUID | None = None,
    ) -> FamilyMemberResponse:
        """Add a member to the family."""
        family = await self._repo.get_by_id(family_id)
        if not family:
            raise NotFoundException("Family", str(family_id))

        # Determine generation dynamically if not provided
        gen = data.generation
        if gen is None:
            if data.relationship_type == "head":
                gen = 0
            elif data.relationship_type == "spouse":
                gen = 0
            elif data.relationship_type in ["son", "daughter", "child"]:
                gen = 1
            elif data.relationship_type in ["father", "mother", "parent"]:
                gen = -1
            elif data.relationship_type == "sibling":
                gen = 0
            else:
                gen = 0

        fm = await self._repo.add_member(
            family_id=family_id,
            member_id=data.member_id,
            relationship_type=data.relationship_type,
            related_to_member_id=data.related_to_member_id,
            generation=gen,
            created_by=created_by,
        )

        # We need the full member data for the response, fetch it via get_family
        # This is slightly inefficient but safe.
        full_family = await self.get_family(family_id)
        for member in full_family.members:
            if member.id == fm.id:
                return member

        raise AppException("Failed to retrieve added family member")

    async def remove_member(self, family_id: UUID, member_id: UUID) -> dict:
        """Remove a member from the family."""
        success = await self._repo.remove_member(family_id, member_id)
        if not success:
            raise NotFoundException("Family Member Link", f"{family_id}-{member_id}")
        return {"message": "Member removed from family"}

    # ── Structured Tree ──────────────────────────────────────────────────

    async def get_family_tree(self, family_id: UUID) -> FamilyTreeResponse:
        """Generate a hierarchical tree of the family."""
        full_family = await self.get_family(family_id)

        if not full_family.members:
            return FamilyTreeResponse(family=full_family, tree=None)

        # Find the head
        head_node = None
        nodes = {}

        # Initialize nodes
        for fm in full_family.members:
            node = FamilyTreeNode(
                member=fm.member, relationship_type=fm.relationship_type, generation=fm.generation, children=[]
            )
            nodes[fm.member_id] = {"node": node, "data": fm}

            # Use explicit family_head_id if available, otherwise fallback to "head" relationship
            if full_family.family_head_id and fm.member_id == full_family.family_head_id:
                head_node = node
            elif not full_family.family_head_id and fm.relationship_type == "head":
                head_node = node

        # If no explicit head, just pick the first member
        if not head_node and nodes:
            head_node = list(nodes.values())[0]["node"]

        # Build tree based on related_to_member_id
        for member_id, info in nodes.items():
            node = info["node"]
            fm_data = info["data"]

            # Skip the root itself
            if node == head_node:
                continue

            parent_id = fm_data.related_to_member_id

            # Fallback logic if related_to is not specified
            if not parent_id:
                if fm_data.relationship_type in ["son", "daughter", "child"]:
                    parent_id = head_node.member.id
                elif fm_data.relationship_type == "spouse":
                    parent_id = head_node.member.id

            # Attach to parent if parent exists
            if parent_id and parent_id in nodes:
                nodes[parent_id]["node"].children.append(node)
            else:
                # If we can't figure out who they are related to, attach to head
                head_node.children.append(node)

        return FamilyTreeResponse(family=full_family, tree=head_node)
