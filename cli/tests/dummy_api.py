import os
from datetime import datetime
from api.app.models.commentfile import CommentFile
from api.app.models.menu import Menu
from api.app.repositories.commentfile import CommentRepository
from api.app.repositories.menu import FileSystemMenuRepository
from api.app.repositories.user import UserRepository
from api.app.models.user import User
from cli.api import PolychromeAPI
from pydantic import SecretStr


class DummyAPI(PolychromeAPI):
    def __init__(self, structure_dir: str):
        self.structure_dir = structure_dir
        self.menu_repository = FileSystemMenuRepository(base_path=os.path.join(structure_dir, "menus"))
        self.comment_repository = CommentRepository(base_path=os.path.join(structure_dir, "commentfiles"))
        self.user_repository = UserRepository()
        self.user_repository.create_user(User(username="testuser", nameline="Quick brown fox", password=SecretStr("testpassword"), email="test@example.com"))
        self.username = "testuser"

    async def get_username(self) -> str | None:
        user = self.user_repository.get_user("testuser")
        if user is None:
            return None
        return user.username

    async def get_user(self, username: str) -> dict[str, str | datetime] | None:
        user = self.user_repository.get_user(username)
        if user is None:
            return None
        return {
            "username": user.username,
            "nameline": user.nameline,
            "created_at": user.created_at
        }

    async def get_menu(self, keypath: str) -> Menu | None:
        return self.menu_repository.get_menu(keypath)

    async def get_comment_file(self, keypath: str) -> CommentFile | None:
        return self.comment_repository.get_comment_file(keypath)