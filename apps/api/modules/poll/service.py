"""
ApnaSamaj – Poll Service

Business logic for managing polls and processing votes securely.
"""

from __future__ import annotations

import logging
import math
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.exceptions import NotFoundException
from apps.api.modules.poll.repository import PollRepository
from apps.api.modules.poll.schemas import (
    PollCreateSchema,
    PollResponse,
    PollVoteSchema,
)

logger = logging.getLogger(__name__)


class PollService:
    """Business logic for polls and voting."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self._repo = PollRepository(session, tenant_id)
        self.tenant_id = tenant_id

    async def create_poll(
        self,
        data: PollCreateSchema,
        created_by: UUID | None = None,
    ) -> PollResponse:
        """Create a new poll with options."""
        payload = data.model_dump(exclude={"options"}, exclude_none=True)
        options_data = [{"text": opt.text} for opt in data.options]

        poll = await self._repo.create(
            data=payload,
            options_data=options_data,
            created_by=created_by,
        )
        logger.info("Poll created: %s", poll.id)
        return PollResponse.model_validate(poll)

    async def get_poll(self, poll_id: UUID) -> PollResponse:
        poll = await self._repo.get_by_id(poll_id)
        if not poll:
            raise NotFoundException("Poll", str(poll_id))
        return PollResponse.model_validate(poll)

    async def list_polls(
        self,
        page: int = 1,
        per_page: int = 20,
    ) -> dict[str, Any]:
        offset = (page - 1) * per_page
        polls, total = await self._repo.get_all_paginated(offset=offset, limit=per_page)

        total_pages = math.ceil(total / per_page) if per_page > 0 else 0
        items = [PollResponse.model_validate(p) for p in polls]

        return {
            "items": items,
            "meta": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
            },
        }

    async def cast_vote(self, poll_id: UUID, data: PollVoteSchema, member_id: UUID) -> dict:
        """Securely cast a vote for a poll option."""
        poll = await self._repo.get_by_id(poll_id)
        if not poll or not poll.is_active:
            raise NotFoundException("Poll", str(poll_id))

        # Check Expiry
        if poll.expires_at < datetime.now(UTC):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This poll has expired and is no longer accepting votes.",
            )

        # Ensure the option belongs to this poll
        valid_options = {str(opt.id) for opt in poll.options}
        if str(data.option_id) not in valid_options:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid option for this poll.")

        # Attempt to cast vote (Repository handles the unique constraint)
        success = await self._repo.cast_vote(poll_id=poll_id, option_id=data.option_id, member_id=member_id)

        if not success:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You have already voted in this poll.")

        logger.info("Vote cast successfully by member %s on poll %s", member_id, poll_id)
        return {"message": "Vote cast successfully"}
