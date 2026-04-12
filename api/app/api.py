from fastapi import APIRouter
from fastapi import Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field

from .auth import get_current_user, verify_credentials, create_access_token
from .login_tracker import login_tracker
from .models.vouch import Vouch, Voucher
from .vouch_tracker import DuplicateVoucherError, vouch_tracker

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class LoggedInUsers(BaseModel):
    users: list[str]


class CreateVouchRequest(BaseModel):
    title: str = Field(min_length=1)
    threshold: int = Field(ge=1)


class VouchesResponse(BaseModel):
    vouches: list[Vouch]


class VoucherResponse(BaseModel):
    voucher: Voucher


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


@router.post("/api/vouches")
async def api_create_vouch(
    payload: CreateVouchRequest,
    username: str = Depends(get_current_user),
) -> Vouch:
    return vouch_tracker.create_vouch(
        title=payload.title.strip(),
        threshold=payload.threshold,
        creator=username,
    )


@router.get("/api/vouches")
async def api_list_vouches(_: str = Depends(get_current_user)) -> VouchesResponse:
    return VouchesResponse(vouches=vouch_tracker.list_vouches())


@router.post("/api/vouches/{vouch_id}/vouchers")
async def api_add_voucher(
    vouch_id: str,
    username: str = Depends(get_current_user),
) -> VoucherResponse:
    vouch = vouch_tracker.get_vouch(vouch_id)
    if vouch is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vouch not found")
    if username == vouch.creator:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Users cannot vouch for themselves",
        )
    try:
        voucher = vouch_tracker.add_voucher(parent_vouch_id=vouch_id, vouched_by=username)
    except DuplicateVoucherError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already vouched for this vouch",
        ) from exc
    if voucher is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vouch not found")
    return VoucherResponse(voucher=voucher)