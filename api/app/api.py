import os
from fastapi import APIRouter
from fastapi import Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from datetime import datetime
from .auth import get_current_user, verify_credentials, create_access_token
from .login_tracker import login_tracker
from .repositories.menu import FileSystemMenuRepository, MenuRepository
from .models.menu import Menu
from .repositories.commentfile import CommentRepository
from .models.commentfile import CommentFile, Post
from .repositories.user import UserRepository, SqlUserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class LoggedInUsers(BaseModel):
    users: list[str]


def get_menu_repository() -> MenuRepository:
    return FileSystemMenuRepository(base_path="data/menus")

def get_comment_repository() -> CommentRepository:
    return CommentRepository(os.environ.get("COMMENT_FILE_PATH", "data/commentfiles"))

def get_user_repository() -> UserRepository:
    return SqlUserRepository()

@router.get("/api/me")
async def api_me(username: str = Depends(get_current_user)) -> TokenData:
    return TokenData(username=username)

@router.post("/api/token")
async def api_token(username: str = Form(...), password: str = Form(...)) -> Token:
    if not verify_credentials(username, password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(username)
    login_tracker.record_login(username, token)
    return Token(access_token=token, token_type="bearer")

class UserInfo(BaseModel):
    username: str
    nameline: str
    created_at: datetime
    last_login: datetime | None = None
    info_text: str | None = None

@router.get("/api/user/{username}")
async def api_user(username: str) -> UserInfo:
    user = get_user_repository().get_user(username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserInfo(username=user.username, nameline=user.nameline, created_at=user.created_at, last_login=user.last_login, info_text=user.info_text)

@router.get("/api/logged-in-users")
async def api_logged_in_users(_: str = Depends(get_current_user)) -> LoggedInUsers:
    return LoggedInUsers(users=login_tracker.get_logged_in_users())

@router.get("/api/menu/{keypath}")
async def api_menu(keypath: str, username: str = Depends(get_current_user), menu_repository: MenuRepository = Depends(get_menu_repository)) -> Menu:
    menu = menu_repository.get_menu(keypath)
    if menu is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu not found")
    return menu

# @router.post("/api/menus")
# async def api_create_menu(menu: Menu, username: str = Depends(get_current_user), menu_repository: MenuRepository = Depends(get_menu_repository)) -> Menu:
#     return menu_repository.create_menu(menu)

# @router.put("/api/menus/{keypath}")
# async def api_update_menu(keypath: str, menu: Menu, username: str = Depends(get_current_user), menu_repository: MenuRepository = Depends(get_menu_repository)) -> Menu:
#     return menu_repository.update_menu(menu)

@router.get("/api/commentfile/{keypath}")
async def api_comment_file(keypath: str, username: str = Depends(get_current_user), comment_repository: CommentRepository = Depends(get_comment_repository)) -> CommentFile:
    comment = comment_repository.get_comment_file(keypath)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment file not found")
    return comment

@router.get("/api/commentfile/{keypath}/posts")
async def api_comment_file_posts(keypath: str, start_index: int = 0, length: int | None = None, username: str = Depends(get_current_user), comment_repository: CommentRepository = Depends(get_comment_repository)) -> list[Post]:
    comment = comment_repository.get_comment_file(keypath)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment file not found")
    return list(comment.read(start_index, length))