from typing import Annotated
from pydantic import BaseModel, StringConstraints
from datetime import datetime

KEYPATH_PATTERN = r"^(_|[a-z0-9]+)$"
KEYPATH = Annotated[str, StringConstraints(to_lower=True, pattern=KEYPATH_PATTERN, min_length=1)]

class MenuItem(BaseModel):
    title: str
    key: Annotated[str, StringConstraints(to_lower=True, pattern=KEYPATH_PATTERN, min_length=1, max_length=1)]
    keypath: KEYPATH | None = None
    item_type: str
    last_change: datetime | None = None
    owner: str | None = None

class Menu(BaseModel):
    title: str
    owner: str
    keypath: KEYPATH
    items: list[MenuItem] = []
    header: str
    access_groups: list[str] | None = None
