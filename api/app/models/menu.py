from pydantic import BaseModel
from datetime import datetime


class MenuItem(BaseModel):
    title: str
    key: str
    item_type: str
    last_change: datetime | None = None
    owner: str | None = None

class Menu(BaseModel):
    title: str
    owner: str | None = None
    keypath: str
    items: list[MenuItem]
    header: str
    access_groups: list[str] | None = None
