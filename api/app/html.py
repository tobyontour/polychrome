from fastapi import APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from pathlib import Path

from .auth import (
    COOKIE_NAME,
    create_access_token,
    get_optional_user,
    get_token_from_request,
    verify_credentials,
)
from .config import ACCESS_TOKEN_EXPIRE_MINUTES, COOKIE_SECURE
from .login_tracker import login_tracker

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=BASE_DIR / "../templates")
router = APIRouter()

def _set_auth_cookie(response: RedirectResponse, token: str) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        path="/",
        secure=COOKIE_SECURE,
    )


def _clear_auth_cookie(response: HTMLResponse | RedirectResponse) -> None:
    response.delete_cookie(key=COOKIE_NAME, path="/", httponly=True, samesite="lax", secure=COOKIE_SECURE)



@router.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    user = get_optional_user(request)
    return templates.TemplateResponse(
        request,
        name="home.html",
        context={"request": request, "user": user},
    )


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str | None = None):
    if get_optional_user(request):
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(
        request,
        name="login.html",
        context={"request": request, "error": error},
    )


@router.post("/login")
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
) -> RedirectResponse:
    if not verify_credentials(username, password):
        return RedirectResponse(
            url="/login?error=1",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    token = create_access_token(username)
    login_tracker.record_login(username, token)
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    _set_auth_cookie(response, token)
    return response


@router.get("/logout", response_class=HTMLResponse)
async def logout_get(request: Request) -> HTMLResponse:
    token = get_token_from_request(request)
    if token:
        login_tracker.record_logout(token)
    response = templates.TemplateResponse(
        request,
        name="logout.html",
        context={"request": request},
    )
    _clear_auth_cookie(response)
    return response


@router.post("/logout")
async def logout_post(request: Request) -> RedirectResponse:
    token = get_token_from_request(request)
    if token:
        login_tracker.record_logout(token)
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    _clear_auth_cookie(response)
    return response
