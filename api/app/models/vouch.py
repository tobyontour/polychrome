from datetime import UTC, datetime

from pydantic import BaseModel, Field


class Voucher(BaseModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    vouched_by: str
    parent_vouch_id: str


class Vouch(BaseModel):
    id: str
    title: str
    threshold: int = Field(ge=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    creator: str
    vouchers: list[Voucher] = Field(default_factory=list)
