from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class PollOption(BaseModel):
    id: str
    title: str
    vote_count: int = Field(default=0, ge=0)


class Vote(BaseModel):
    poll_id: str
    voter: str
    option_id: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)


class Poll(BaseModel):
    id: str
    owner: str
    title: str
    description: str
    is_anonymous: bool = False
    closes_at: datetime
    created_at: datetime = Field(default_factory=datetime.now)
    options: list[PollOption] = Field(min_length=2)

    @model_validator(mode="after")
    def validate_poll(self) -> "Poll":
        if self.closes_at <= self.created_at:
            raise ValueError("Poll closes_at must be after created_at")

        option_ids = [option.id for option in self.options]
        if len(option_ids) != len(set(option_ids)):
            raise ValueError("Poll option ids must be unique")

        return self
