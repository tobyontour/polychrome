from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Callable, Protocol

from pydantic import BaseModel, Field
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, Session, declarative_base, mapped_column, relationship

from ..config import get_session
from ..models.poll import Poll, PollOption, Vote


class PollRepositoryInterface(Protocol):
    def get_poll(self, poll_id: str) -> Poll | None:
        ...

    def list_polls(self) -> list[Poll]:
        ...

    def create_poll(self, poll: Poll) -> None:
        ...

    def update_poll(self, poll: Poll) -> None:
        ...

    def delete_poll(self, poll_id: str) -> None:
        ...

    def record_vote(self, poll_id: str, voter: str, option_id: str) -> Vote:
        ...

    def get_vote(self, poll_id: str, voter: str) -> Vote | None:
        ...

    def list_votes(self, poll_id: str) -> list[Vote]:
        ...


class PollStorageFile(BaseModel):
    polls: dict[str, Poll] = Field(default_factory=dict)
    votes: list[Vote] = Field(default_factory=list)


class FilePollRepository:
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.index_path = os.path.join(base_path, "polls.json")

    def _load_storage(self) -> PollStorageFile:
        if not os.path.exists(self.index_path):
            return PollStorageFile()
        with open(self.index_path, "r", encoding="utf-8") as handle:
            content = json.load(handle)
        return PollStorageFile.model_validate(content)

    def _save_storage(self, storage: PollStorageFile) -> None:
        os.makedirs(self.base_path, exist_ok=True)
        with open(self.index_path, "w", encoding="utf-8") as handle:
            handle.write(storage.model_dump_json(indent=2))

    def get_poll(self, poll_id: str) -> Poll | None:
        return self._load_storage().polls.get(poll_id)

    def list_polls(self) -> list[Poll]:
        storage = self._load_storage()
        return list(storage.polls.values())

    def create_poll(self, poll: Poll) -> None:
        storage = self._load_storage()
        if poll.id in storage.polls:
            raise ValueError(f"Poll already exists: {poll.id}")
        storage.polls[poll.id] = poll
        self._save_storage(storage)

    def update_poll(self, poll: Poll) -> None:
        storage = self._load_storage()
        if poll.id not in storage.polls:
            raise ValueError(f"Poll not found: {poll.id}")
        storage.polls[poll.id] = poll
        self._save_storage(storage)

    def delete_poll(self, poll_id: str) -> None:
        storage = self._load_storage()
        storage.polls.pop(poll_id, None)
        storage.votes = [vote for vote in storage.votes if vote.poll_id != poll_id]
        self._save_storage(storage)

    def record_vote(self, poll_id: str, voter: str, option_id: str) -> Vote:
        storage = self._load_storage()
        poll = storage.polls.get(poll_id)
        if poll is None:
            raise ValueError(f"Poll not found: {poll_id}")

        if any(vote.poll_id == poll_id and vote.voter == voter for vote in storage.votes):
            raise ValueError(f"Voter already voted in poll: {poll_id}")

        target_option = next((option for option in poll.options if option.id == option_id), None)
        if target_option is None:
            raise ValueError(f"Option not found in poll: {option_id}")

        target_option.vote_count += 1
        stored_option_id = None if poll.is_anonymous else option_id
        vote = Vote(poll_id=poll_id, voter=voter, option_id=stored_option_id)
        storage.votes.append(vote)
        storage.polls[poll_id] = poll
        self._save_storage(storage)
        return vote

    def get_vote(self, poll_id: str, voter: str) -> Vote | None:
        storage = self._load_storage()
        return next(
            (vote for vote in storage.votes if vote.poll_id == poll_id and vote.voter == voter),
            None,
        )

    def list_votes(self, poll_id: str) -> list[Vote]:
        storage = self._load_storage()
        return [vote for vote in storage.votes if vote.poll_id == poll_id]


PollBase = declarative_base()


class SqlPoll(PollBase):
    __tablename__ = "polls"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    owner: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    is_anonymous: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    closes_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    options: Mapped[list["SqlPollOption"]] = relationship(
        back_populates="poll",
        cascade="all, delete-orphan",
        order_by="SqlPollOption.position",
    )

    votes: Mapped[list["SqlVote"]] = relationship(
        back_populates="poll",
        cascade="all, delete-orphan",
    )

    def to_model(self) -> Poll:
        return Poll(
            id=self.id,
            owner=self.owner,
            title=self.title,
            description=self.description,
            is_anonymous=self.is_anonymous,
            closes_at=self.closes_at,
            created_at=self.created_at,
            options=[option.to_model() for option in self.options],
        )

    def from_model(self, poll: Poll) -> None:
        self.id = poll.id
        self.owner = poll.owner
        self.title = poll.title
        self.description = poll.description
        self.is_anonymous = poll.is_anonymous
        self.closes_at = poll.closes_at
        self.created_at = poll.created_at
        self.options = [
            SqlPollOption.from_model(self.id, option, position)
            for position, option in enumerate(poll.options)
        ]


class SqlPollOption(PollBase):
    __tablename__ = "poll_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    poll_id: Mapped[str] = mapped_column(String, ForeignKey("polls.id"), nullable=False)
    option_id: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    vote_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    poll: Mapped[SqlPoll] = relationship(back_populates="options")

    __table_args__ = (UniqueConstraint("poll_id", "option_id", name="uq_poll_option_id"),)

    def to_model(self) -> PollOption:
        return PollOption(id=self.option_id, title=self.title, vote_count=self.vote_count)

    @classmethod
    def from_model(cls, poll_id: str, option: PollOption, position: int) -> "SqlPollOption":
        return cls(
            poll_id=poll_id,
            option_id=option.id,
            title=option.title,
            vote_count=option.vote_count,
            position=position,
        )


class SqlVote(PollBase):
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    poll_id: Mapped[str] = mapped_column(String, ForeignKey("polls.id"), nullable=False)
    voter: Mapped[str] = mapped_column(String, nullable=False)
    option_id: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    poll: Mapped[SqlPoll] = relationship(back_populates="votes")

    __table_args__ = (UniqueConstraint("poll_id", "voter", name="uq_vote_poll_voter"),)

    def to_model(self) -> Vote:
        return Vote(
            poll_id=self.poll_id,
            voter=self.voter,
            option_id=self.option_id,
            created_at=self.created_at,
        )


class SqlAlchemyPollRepository:
    def __init__(self, session_factory: Callable[[], Session] = get_session):
        self._session_factory = session_factory
        with self._session_factory() as session:
            PollBase.metadata.create_all(bind=session.get_bind())

    def get_poll(self, poll_id: str) -> Poll | None:
        with self._session_factory() as session:
            poll = session.query(SqlPoll).filter(SqlPoll.id == poll_id).first()
            if poll is None:
                return None
            return poll.to_model()

    def list_polls(self) -> list[Poll]:
        with self._session_factory() as session:
            polls = session.query(SqlPoll).order_by(SqlPoll.created_at.asc()).all()
            return [poll.to_model() for poll in polls]

    def create_poll(self, poll: Poll) -> None:
        with self._session_factory() as session:
            existing = session.query(SqlPoll).filter(SqlPoll.id == poll.id).first()
            if existing is not None:
                raise ValueError(f"Poll already exists: {poll.id}")
            sql_poll = SqlPoll()
            sql_poll.from_model(poll)
            session.add(sql_poll)
            session.commit()

    def update_poll(self, poll: Poll) -> None:
        with self._session_factory() as session:
            sql_poll = session.query(SqlPoll).filter(SqlPoll.id == poll.id).first()
            if sql_poll is None:
                raise ValueError(f"Poll not found: {poll.id}")
            sql_poll.from_model(poll)
            session.commit()

    def delete_poll(self, poll_id: str) -> None:
        with self._session_factory() as session:
            sql_poll = session.query(SqlPoll).filter(SqlPoll.id == poll_id).first()
            if sql_poll is None:
                return
            session.delete(sql_poll)
            session.commit()

    def record_vote(self, poll_id: str, voter: str, option_id: str) -> Vote:
        with self._session_factory() as session:
            poll = session.query(SqlPoll).filter(SqlPoll.id == poll_id).first()
            if poll is None:
                raise ValueError(f"Poll not found: {poll_id}")

            existing_vote = (
                session.query(SqlVote)
                .filter(SqlVote.poll_id == poll_id, SqlVote.voter == voter)
                .first()
            )
            if existing_vote is not None:
                raise ValueError(f"Voter already voted in poll: {poll_id}")

            target_option = next(
                (option for option in poll.options if option.option_id == option_id),
                None,
            )
            if target_option is None:
                raise ValueError(f"Option not found in poll: {option_id}")

            target_option.vote_count += 1
            stored_option_id = None if poll.is_anonymous else option_id
            sql_vote = SqlVote(
                poll_id=poll_id,
                voter=voter,
                option_id=stored_option_id,
                created_at=datetime.now(),
            )
            session.add(sql_vote)
            session.commit()
            return sql_vote.to_model()

    def get_vote(self, poll_id: str, voter: str) -> Vote | None:
        with self._session_factory() as session:
            vote = (
                session.query(SqlVote)
                .filter(SqlVote.poll_id == poll_id, SqlVote.voter == voter)
                .first()
            )
            if vote is None:
                return None
            return vote.to_model()

    def list_votes(self, poll_id: str) -> list[Vote]:
        with self._session_factory() as session:
            votes = session.query(SqlVote).filter(SqlVote.poll_id == poll_id).all()
            return [vote.to_model() for vote in votes]
