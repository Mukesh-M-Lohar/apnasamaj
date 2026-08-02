"""
ApnaSamaj – Polling Models

Defines polls, options, and secure voting logic ensuring one-vote-per-member.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, String, Text
from sqlalchemy import Column, DateTime, UniqueConstraint

from apps.api.core.models.base import BaseModel

if TYPE_CHECKING:
    from apps.api.modules.member.models import Member
    from apps.api.modules.committee.models import Committee


class Poll(BaseModel, table=True):
    """A community vote/survey."""
    __tablename__ = "polls"

    question: str = Field(sa_column=Column(String(500), nullable=False))
    description: str | None = Field(default=None, sa_column=Column(Text))
    
    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    is_active: bool = Field(default=True)

    # Optional: restricts poll to a specific committee
    target_committee_id: UUID | None = Field(default=None, foreign_key="committees.id")

    # Relationships
    options: list["PollOption"] = Relationship(back_populates="poll")
    votes: list["PollVote"] = Relationship(back_populates="poll")
    target_committee: "Committee" = Relationship()


class PollOption(BaseModel, table=True):
    """An option to choose within a poll."""
    __tablename__ = "poll_options"

    poll_id: UUID = Field(foreign_key="polls.id", nullable=False)
    text: str = Field(sa_column=Column(String(255), nullable=False))
    
    # Cache the vote count for performance (incremented carefully)
    vote_count: int = Field(default=0)

    poll: Poll = Relationship(back_populates="options")
    votes: list["PollVote"] = Relationship(back_populates="option")


class PollVote(BaseModel, table=True):
    """A member's casted vote."""
    __tablename__ = "poll_votes"
    
    __table_args__ = (
        # Ensure a member can only vote once per poll!
        UniqueConstraint("poll_id", "member_id", name="uix_one_vote_per_member"),
    )

    poll_id: UUID = Field(foreign_key="polls.id", nullable=False)
    option_id: UUID = Field(foreign_key="poll_options.id", nullable=False)
    member_id: UUID = Field(foreign_key="members.id", nullable=False)

    poll: Poll = Relationship(back_populates="votes")
    option: PollOption = Relationship(back_populates="votes")
    member: "Member" = Relationship()
