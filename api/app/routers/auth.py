from fastapi import APIRouter, Form, HTTPException, status
from api.app.auth import verify_credentials, create_access_token
from api.app.login_tracker import login_tracker
from .api import Token

router = APIRouter()
@router.post("/api/token")
async def token_post(username: str = Form(...), password: str = Form(...)) -> Token:
    if not verify_credentials(username, password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(username)
    login_tracker.record_login(username, token)
    return Token(access_token=token, token_type="bearer")