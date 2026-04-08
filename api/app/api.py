from fastapi import APIRouter
from fastapi import Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from .auth import get_current_user, verify_credentials, create_access_token
from .login_tracker import login_tracker

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class LoggedInUsers(BaseModel):
    users: list[str]


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