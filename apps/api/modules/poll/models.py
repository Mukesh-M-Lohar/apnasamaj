"""
ApnaSamaj – Polling Models

Defines polls, options, and secure voting logic ensuring one-vote-per-member.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.api.core.base_model import BaseModel

if TYPE_CHECKING:
    from apps.api.modules.member.models import Member
    from apps.api.modules.committee.models import Committee


class Poll(BaseModel):
    """A community vote/survey."""

    __tablename__ = "polls"

    question: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(default=True)

    # Optional: restricts poll to a specific committee
    target_committee_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("committees.id"), nullable=True
    )

    # Relationships
    options: Mapped[list["PollOption"]] = relationship(back_populates="poll")
    votes: Mapped[list["PollVote"]] = relationship(back_populates="poll")
    target_committee: Mapped["Committee"] = relationship()


class PollOption(BaseModel):
    """An option to choose within a poll."""

    __tablename__ = "poll_options"

    poll_id: Mapped[UUID] = mapped_column(ForeignKey("polls.id"), nullable=False)
    text: Mapped[str] = mapped_column(String(255), nullable=False)

    # Cache the vote count for performance (incremented carefully)
    vote_count: Mapped[int] = mapped_column(default=0)

    poll: Mapped[Poll] = relationship(back_populates="options")
    votes: Mapped[list["PollVote"]] = relationship(back_populates="option")


class PollVote(BaseModel):
    """A member's casted vote."""

    __tablename__ = "poll_votes"

    __table_args__ = (
        # Ensure a member can only vote once per poll!
        UniqueConstraint("poll_id", "member_id", name="uix_one_vote_per_member"),
    )

    poll_id: Mapped[UUID] = mapped_column(ForeignKey("polls.id"), nullable=False)
    option_id: Mapped[UUID] = mapped_column(
        ForeignKey("poll_options.id"), nullable=False
    )
    member_id: Mapped[UUID] = mapped_column(ForeignKey("members.id"), nullable=False)

    poll: Mapped[Poll] = relationship(back_populates="votes")
    option: Mapped[PollOption] = relationship(back_populates="votes")
    member: Mapped["Member"] = relationship()
