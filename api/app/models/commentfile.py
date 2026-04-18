from pydantic import BaseModel
from datetime import datetime
from .menu import KEYPATH
from typing import Generator

class Post(BaseModel):
    date: datetime
    from_line: str
    subject: str
    content: str
    author: str
    index: int

class CommentFile(BaseModel):
    keypath: KEYPATH
    name: str
    header: str
    last_change: datetime
    owner: str
    access_groups: list[str] | None = None
    posts: list[Post] = []

    def read(self, start_index: int, length: int | None = None) -> Generator[Post, None, None]:
        if length is not None:
            for post in self.posts[start_index:start_index+length]:
                yield post
        else:
            for post in self.posts[start_index:]:
                yield post

    def append(self, post: Post) -> None:
        post.index = len(self.posts)
        self.posts.append(post)