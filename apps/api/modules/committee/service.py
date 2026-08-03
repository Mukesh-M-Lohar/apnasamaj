"""
ApnaSamaj – Committee Service

Business logic for committee management and term tracking.
"""

from __future__ import annotations

import logging
import math
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.exceptions import AppException, NotFoundException
from apps.api.modules.committee.repository import CommitteeRepository
from apps.api.modules.committee.schemas import (
    AddCommitteeMemberSchema,
    CommitteeCreateSchema,
    CommitteeMemberResponse,
    CommitteeResponse,
    CommitteeUpdateSchema,
)
from apps.api.modules.member.schemas import MemberListResponse

logger = logging.getLogger(__name__)


class CommitteeService:
    """Business logic for committee management."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self._repo = CommitteeRepository(session, tenant_id)

    # ── Create ───────────────────────────────────────────────────────────

    async def create_committee(
        self,
        data: CommitteeCreateSchema,
        created_by: UUID | None = None,
    ) -> CommitteeResponse:
        """Create a new committee."""
        committee = await self._repo.create(
            data=data.model_dump(exclude_none=True),
            created_by=created_by,
        )
        logger.info("Committee created: %s", committee.name)
        return await self.get_committee(committee.id)

    # ── Read ─────────────────────────────────────────────────────────────

    async def get_committee(self, committee_id: UUID) -> CommitteeResponse:
        """Get a committee with its members."""
        committee = await self._repo.get_by_id(committee_id)
        if not committee:
            raise NotFoundException("Committee", str(committee_id))

        members_data = await self._repo.get_committee_members(committee_id)

        members = []
        for cm in members_data:
            member_summary = MemberListResponse.model_validate(cm.member_obj)
            members.append(
                CommitteeMemberResponse(
                    id=cm.id,
                    committee_id=cm.committee_id,
                    member_id=cm.member_id,
                    position=cm.position,
                    responsibilities=cm.responsibilities,
                    joined_date=cm.joined_date,
                    left_date=cm.left_date,
                    status=cm.status,
                    member=member_summary,
                )
            )

        response = CommitteeResponse.model_validate(committee)
        response.members = members
        return response

    async def list_committees(
        self,
        page: int = 1,
        per_page: int = 20,
        search: str | None = None,
        status: str | None = None,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> dict[str, Any]:
        """List committees with pagination and filtering."""
        offset = (page - 1) * per_page

        committees, total = await self._repo.get_all_paginated(
            offset=offset,
            limit=per_page,
            search=search,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        total_pages = math.ceil(total / per_page) if per_page > 0 else 0

        # We don't fetch members for the list view to keep it lightweight.
        items = [CommitteeResponse.model_validate(c) for c in committees]

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

    async def update_committee(
        self,
        committee_id: UUID,
        data: CommitteeUpdateSchema,
        updated_by: UUID | None = None,
    ) -> CommitteeResponse:
        """Update a committee."""
        committee = await self._repo.update(
            committee_id=committee_id,
            data=data.model_dump(exclude_unset=True),
            updated_by=updated_by,
        )
        if not committee:
            raise NotFoundException("Committee", str(committee_id))

        return await self.get_committee(committee_id)

    # ── Delete ───────────────────────────────────────────────────────────

    async def delete_committee(self, committee_id: UUID, deleted_by: UUID | None = None) -> dict:
        """Soft-delete a committee."""
        success = await self._repo.soft_delete(committee_id, deleted_by)
        if not success:
            raise NotFoundException("Committee", str(committee_id))
        logger.info("Committee soft-deleted: %s by %s", committee_id, deleted_by)
        return {"message": "Committee deleted successfully"}

    # ── Members (Junction) ───────────────────────────────────────────────

    async def add_member(
        self,
        committee_id: UUID,
        data: AddCommitteeMemberSchema,
        created_by: UUID | None = None,
    ) -> CommitteeMemberResponse:
        """Add a member to the committee."""
        committee = await self._repo.get_by_id(committee_id)
        if not committee:
            raise NotFoundException("Committee", str(committee_id))

        cm = await self._repo.add_member(
            committee_id=committee_id,
            member_id=data.member_id,
            position=data.position,
            responsibilities=data.responsibilities,
            joined_date=data.joined_date,
            left_date=data.left_date,
            status=data.status,
            created_by=created_by,
        )

        # Need the full member payload
        full_committee = await self.get_committee(committee_id)
        for member in full_committee.members:
            if member.id == cm.id:
                return member

        raise AppException("Failed to retrieve added committee member")

    async def remove_member(self, committee_id: UUID, member_id: UUID) -> dict:
        """Remove a member from the committee."""
        success = await self._repo.remove_member(committee_id, member_id)
        if not success:
            raise NotFoundException("Committee Member Link", f"{committee_id}-{member_id}")
        return {"message": "Member removed from committee"}
