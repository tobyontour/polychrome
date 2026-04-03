import secrets
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, Request, status
from jose import JWTError, jwt

from .config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, AUTH_PASSWORD, AUTH_USERNAME, SECRET_KEY

COOKIE_NAME = "access_token"


def verify_credentials(username: str, password: str) -> bool:
    user_ok = secrets.compare_digest(username.encode("utf-8"), AUTH_USERNAME.encode("utf-8"))
    pass_ok = secrets.compare_digest(password.encode("utf-8"), AUTH_PASSWORD.encode("utf-8"))
    return user_ok and pass_ok


def create_access_token(subject: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": subject, "exp": int(expire.timestamp())}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if isinstance(sub, str):
            return sub
    except JWTError:
        return None
    return None


def get_token_from_request(request: Request) -> str | None:
    return request.cookies.get(COOKIE_NAME)


def get_token_from_header(request: Request) -> str | None:
    authorization = request.headers.get("Authorization")
    if not authorization:
        return None
    if not authorization.startswith("Bearer "):
        return None
    return authorization.split(" ")[1]

def get_optional_user(request: Request) -> str | None:
    token = get_token_from_request(request)
    if not token:
        token = get_token_from_header(request)
    if not token:
        return None
    return decode_token(token)


async def get_current_user(request: Request) -> str:
    username = get_optional_user(request)
    if username is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return username
