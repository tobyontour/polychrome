from pydantic import BaseModel
from datetime import datetime

class Post(BaseModel):
    date: datetime
    from_line: str
    subject: str
    content: str
    author: str

class File(BaseModel):
    name: str
    header: str
    path: str
    last_change: datetime
    owner: str
    access_groups: list[str] | None = None

