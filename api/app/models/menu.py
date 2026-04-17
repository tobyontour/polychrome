from typing import Annotated
from pydantic import BaseModel, StringConstraints
from datetime import datetime

KEYPATH_PATTERN = r"^[a-z0-9_]+$"

class MenuItem(BaseModel):
    title: str
    key: Annotated[str, StringConstraints(to_lower=True, pattern=KEYPATH_PATTERN, min_length=1, max_length=1)]
    item_type: str
    last_change: datetime | None = None
    owner: str | None = None

class Menu(BaseModel):
    title: str
    owner: str
    keypath: Annotated[str, StringConstraints(to_lower=True, pattern=KEYPATH_PATTERN, min_length=1)]
    items: list[MenuItem] = []
    header: str
    access_groups: list[str] | None = None
