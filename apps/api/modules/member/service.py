"""
ApnaSamaj – Member Service

Business logic for member management.
Ensures tenant isolation and handles complex lookups.
"""

from __future__ import annotations

import logging
import math
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.exceptions import (
    NotFoundException,
)
from apps.api.modules.member.repository import MemberRepository
from apps.api.modules.member.schemas import (
    MemberCreateSchema,
    MemberListResponse,
    MemberResponse,
    MemberUpdateSchema,
)

logger = logging.getLogger(__name__)


class MemberService:
    """Business logic for community members."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self._repo = MemberRepository(session, tenant_id)

    # ── Create ───────────────────────────────────────────────────────────

    async def create_member(
        self,
        data: MemberCreateSchema,
        created_by: UUID | None = None,
    ) -> MemberResponse:
        """Create a new member profile."""
        member = await self._repo.create(
            data=data.model_dump(exclude_none=True),
            created_by=created_by,
        )
        logger.info("Member created: %s %s", member.first_name, member.last_name)
        return MemberResponse.model_validate(member)

    # ── Read ─────────────────────────────────────────────────────────────

    async def get_member(self, member_id: UUID) -> MemberResponse:
        """Get a single member by ID."""
        member = await self._repo.get_by_id(member_id)
        if not member:
            raise NotFoundException("Member", str(member_id))
        return MemberResponse.model_validate(member)

    async def get_member_by_user(self, user_id: UUID) -> MemberResponse:
        """Get the member profile associated with a user ID."""
        member = await self._repo.get_by_user_id(user_id)
        if not member:
            raise NotFoundException("Member profile for user", str(user_id))
        return MemberResponse.model_validate(member)

    async def list_members(
        self,
        page: int = 1,
        per_page: int = 20,
        search: str | None = None,
        status: str | None = None,
        blood_group: str | None = None,
        city: str | None = None,
        gender: str | None = None,
        sort_by: str = "first_name",
        sort_order: str = "asc",
    ) -> dict[str, Any]:
        """List members for the directory with pagination and filters."""
        offset = (page - 1) * per_page

        members, total = await self._repo.get_all_paginated(
            offset=offset,
            limit=per_page,
            search=search,
            status=status,
            blood_group=blood_group,
            city=city,
            gender=gender,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        total_pages = math.ceil(total / per_page) if per_page > 0 else 0

        items = [MemberListResponse.model_validate(m) for m in members]

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

    async def update_member(
        self,
        member_id: UUID,
        data: MemberUpdateSchema,
        updated_by: UUID | None = None,
    ) -> MemberResponse:
        """Partially update a member profile."""
        member = await self._repo.update(
            member_id=member_id,
            data=data.model_dump(exclude_unset=True),
            updated_by=updated_by,
        )
        if not member:
            raise NotFoundException("Member", str(member_id))

        logger.info("Member updated: %s", member_id)
        return MemberResponse.model_validate(member)

    # ── Delete ───────────────────────────────────────────────────────────

    async def delete_member(self, member_id: UUID, deleted_by: UUID | None = None) -> dict:
        """Soft-delete a member."""
        success = await self._repo.soft_delete(member_id, deleted_by)
        if not success:
            raise NotFoundException("Member", str(member_id))
        logger.info("Member soft-deleted: %s by %s", member_id, deleted_by)
        return {"message": "Member deleted successfully"}

    # ── Bulk Import ──────────────────────────────────────────────────────

    async def bulk_import_members(
        self,
        file_content: bytes,
        created_by: UUID | None = None,
    ) -> dict:
        """Parse CSV and bulk import members."""
        import csv
        import io

        from pydantic import ValidationError

        # Decode and parse CSV
        text_content = file_content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text_content))

        total_rows = 0
        success_count = 0
        errors = []

        for row in reader:
            total_rows += 1
            try:
                # Clean up empty strings to None
                cleaned_row = {k: (v.strip() if v.strip() else None) for k, v in row.items()}

                # Parse through Pydantic to validate
                schema = MemberCreateSchema(**cleaned_row)

                # Create in DB
                await self._repo.create(
                    data=schema.model_dump(exclude_none=True),
                    created_by=created_by,
                )
                success_count += 1
            except ValidationError as e:
                # Capture validation errors
                err_msg = ", ".join([f"{err['loc'][0]}: {err['msg']}" for err in e.errors()])
                errors.append({"row": total_rows, "error": err_msg, "data": cleaned_row})
            except Exception as e:
                errors.append({"row": total_rows, "error": str(e), "data": row})

        return {"total_rows": total_rows, "success_count": success_count, "error_count": len(errors), "errors": errors}
