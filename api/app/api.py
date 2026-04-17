from fastapi import APIRouter
from fastapi import Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from .auth import get_current_user, verify_credentials, create_access_token
from .login_tracker import login_tracker
from .repositories.menu import FileSystemMenuRepository, MenuRepository
from .models.menu import Menu

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