"""
ApnaSamaj – Poll Repository

Database operations for handling polls and safely casting votes.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import Select, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from apps.api.modules.poll.models import Poll, PollOption, PollVote


class PollRepository:
    """Handles poll DB operations scoped to a tenant."""

    def __init__(self, session: AsyncSession, tenant_id: UUID) -> None:
        self._session = session
        self.tenant_id = tenant_id

    def _base_query(self) -> Select:
        return (
            select(Poll)
            .options(selectinload(Poll.options))
            .where(
                Poll.tenant_id == self.tenant_id,
                Poll.is_deleted == False,  # noqa: E712
            )
        )

    # ── Polls ────────────────────────────────────────────────────────────

    async def create(
        self, data: dict[str, Any], options_data: list[dict[str, str]], created_by: UUID | None = None
    ) -> Poll:
        poll = Poll(
            tenant_id=self.tenant_id,
            created_by=created_by,
            updated_by=created_by,
            **data,
        )
        self._session.add(poll)
        await self._session.flush()

        for opt in options_data:
            option = PollOption(
                tenant_id=self.tenant_id,
                poll_id=poll.id,
                text=opt["text"],
                created_by=created_by,
                updated_by=created_by,
            )
            self._session.add(option)

        await self._session.flush()

        # Load relationships
        await self._session.refresh(poll)

        stmt = self._base_query().where(Poll.id == poll.id)
        res = await self._session.execute(stmt)
        return res.scalar_one()

    async def get_by_id(self, poll_id: UUID) -> Poll | None:
        stmt = self._base_query().where(Poll.id == poll_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_paginated(self, offset: int = 0, limit: int = 20) -> tuple[list[Poll], int]:
        stmt = self._base_query()
        count_stmt = (
            select(func.count())
            .select_from(Poll)
            .where(
                Poll.tenant_id == self.tenant_id,
                Poll.is_deleted == False,  # noqa: E712
            )
        )

        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = stmt.order_by(Poll.created_at.desc())
        stmt = stmt.offset(offset).limit(limit)

        result = await self._session.execute(stmt)
        polls = list(result.scalars().all())

        return polls, total

    # ── Voting ───────────────────────────────────────────────────────────

    async def has_voted(self, poll_id: UUID, member_id: UUID) -> bool:
        stmt = select(PollVote).where(
            PollVote.poll_id == poll_id, PollVote.member_id == member_id, PollVote.tenant_id == self.tenant_id
        )
        result = await self._session.execute(stmt)
        return result.first() is not None

    async def cast_vote(self, poll_id: UUID, option_id: UUID, member_id: UUID) -> bool:
        """
        Cast a vote. Returns True if successful.
        Relies on the DB UniqueConstraint to prevent double-voting.
        """
        try:
            vote = PollVote(
                tenant_id=self.tenant_id,
                poll_id=poll_id,
                option_id=option_id,
                member_id=member_id,
                created_by=member_id,
                updated_by=member_id,
            )
            self._session.add(vote)

            # Increment the denormalized counter
            stmt = (
                update(PollOption)
                .where(PollOption.id == option_id, PollOption.poll_id == poll_id)
                .values(vote_count=PollOption.vote_count + 1)
            )
            await self._session.execute(stmt)
            await self._session.flush()
            return True

        except IntegrityError:
            await self._session.rollback()
            return False
