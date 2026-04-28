from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from api.app.models.poll import Poll, PollOption
from api.app.repositories.poll import FilePollRepository, SqlAlchemyPollRepository


def _poll(
    poll_id: str = "poll-1",
    *,
    is_anonymous: bool = False,
    title: str = "Lunch vote",
) -> Poll:
    created_at = datetime(2026, 1, 1, 12, 0, 0)
    return Poll(
        id=poll_id,
        owner="alice",
        title=title,
        description="Choose what we should have for lunch.",
        is_anonymous=is_anonymous,
        closes_at=created_at + timedelta(hours=4),
        created_at=created_at,
        options=[
            PollOption(id="pizza", title="Pizza"),
            PollOption(id="sushi", title="Sushi"),
        ],
    )


@pytest.fixture(params=["file", "sql"])
def poll_repo(request: pytest.FixtureRequest, tmp_path):
    if request.param == "file":
        return FilePollRepository(str(tmp_path / "poll-data"))

    engine = create_engine(f"sqlite:///{tmp_path / 'polls.db'}")

    def session_factory() -> Session:
        return Session(bind=engine)

    return SqlAlchemyPollRepository(session_factory=session_factory)


def test_poll_requires_unique_option_ids() -> None:
    created_at = datetime(2026, 1, 1, 12, 0, 0)
    with pytest.raises(ValueError, match="unique"):
        Poll(
            id="poll-1",
            owner="alice",
            title="Lunch vote",
            description="Choose lunch.",
            is_anonymous=False,
            closes_at=created_at + timedelta(hours=1),
            created_at=created_at,
            options=[
                PollOption(id="pizza", title="Pizza"),
                PollOption(id="pizza", title="More Pizza"),
            ],
        )


def test_poll_requires_closes_at_after_created_at() -> None:
    created_at = datetime(2026, 1, 1, 12, 0, 0)
    with pytest.raises(ValueError, match="closes_at must be after created_at"):
        Poll(
            id="poll-1",
            owner="alice",
            title="Lunch vote",
            description="Choose lunch.",
            is_anonymous=False,
            closes_at=created_at,
            created_at=created_at,
            options=[
                PollOption(id="pizza", title="Pizza"),
                PollOption(id="sushi", title="Sushi"),
            ],
        )


def test_poll_repository_crud(poll_repo) -> None:
    poll = _poll()
    poll_repo.create_poll(poll)

    assert poll_repo.get_poll(poll.id) == poll
    assert poll_repo.list_polls() == [poll]

    poll.title = "Updated lunch vote"
    poll_repo.update_poll(poll)

    updated = poll_repo.get_poll(poll.id)
    assert updated is not None
    assert updated.title == "Updated lunch vote"

    poll_repo.delete_poll(poll.id)
    assert poll_repo.get_poll(poll.id) is None
    assert poll_repo.list_polls() == []


def test_poll_repository_records_named_vote(poll_repo) -> None:
    poll = _poll(is_anonymous=False)
    poll_repo.create_poll(poll)

    vote = poll_repo.record_vote(poll.id, "bob", "pizza")
    assert vote.option_id == "pizza"

    stored_vote = poll_repo.get_vote(poll.id, "bob")
    assert stored_vote is not None
    assert stored_vote.option_id == "pizza"

    votes = poll_repo.list_votes(poll.id)
    assert len(votes) == 1
    assert votes[0].voter == "bob"

    updated_poll = poll_repo.get_poll(poll.id)
    assert updated_poll is not None
    assert updated_poll.options[0].vote_count == 1
    assert updated_poll.options[1].vote_count == 0


def test_poll_repository_records_anonymous_vote_without_option_id(poll_repo) -> None:
    poll = _poll(is_anonymous=True)
    poll_repo.create_poll(poll)

    vote = poll_repo.record_vote(poll.id, "bob", "sushi")
    assert vote.option_id is None

    stored_vote = poll_repo.get_vote(poll.id, "bob")
    assert stored_vote is not None
    assert stored_vote.option_id is None

    updated_poll = poll_repo.get_poll(poll.id)
    assert updated_poll is not None
    assert updated_poll.options[0].vote_count == 0
    assert updated_poll.options[1].vote_count == 1


def test_poll_repository_prevents_duplicate_votes_from_same_user(poll_repo) -> None:
    poll = _poll()
    poll_repo.create_poll(poll)
    poll_repo.record_vote(poll.id, "bob", "pizza")

    with pytest.raises(ValueError, match="already voted"):
        poll_repo.record_vote(poll.id, "bob", "sushi")


def test_poll_repository_rejects_unknown_option_id(poll_repo) -> None:
    poll = _poll()
    poll_repo.create_poll(poll)

    with pytest.raises(ValueError, match="Option not found"):
        poll_repo.record_vote(poll.id, "bob", "tacos")


def test_poll_repository_delete_poll_removes_votes(poll_repo) -> None:
    poll = _poll()
    poll_repo.create_poll(poll)
    poll_repo.record_vote(poll.id, "bob", "pizza")
    poll_repo.record_vote(poll.id, "carol", "sushi")

    poll_repo.delete_poll(poll.id)

    assert poll_repo.get_vote(poll.id, "bob") is None
    assert poll_repo.list_votes(poll.id) == []
