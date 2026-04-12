"""Tests for JSON API routes in api.app.api."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from jose import jwt

from api.app.api import router
from api.app.auth import COOKIE_NAME, create_access_token
from api.app.config import ALGORITHM, SECRET_KEY


@pytest.fixture
def api_client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_token_success_returns_bearer_jwt(api_client: TestClient) -> None:
    response = api_client.post(
        "/api/token",
        data={"username": "testuser", "password": "testpass"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert "access_token" in body
    payload = jwt.decode(body["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "testuser"


@pytest.mark.parametrize(
    "username,password",
    [("testuser", "wrong"), ("other", "testpass")],
)
def test_token_invalid_credentials_401(
    api_client: TestClient,
    username: str,
    password: str,
) -> None:
    response = api_client.post(
        "/api/token",
        data={"username": username, "password": password},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_me_without_credentials_401(api_client: TestClient) -> None:
    response = api_client.get("/api/me")
    assert response.status_code == 401


def test_me_with_bearer_token(api_client: TestClient) -> None:
    token_response = api_client.post(
        "/api/token",
        data={"username": "testuser", "password": "testpass"},
    )
    token = token_response.json()["access_token"]
    me = api_client.get(
        "/api/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me.status_code == 200
    assert me.json() == {"username": "testuser"}


def test_me_rejects_malformed_authorization_header(api_client: TestClient) -> None:
    response = api_client.get(
        "/api/me",
        headers={"Authorization": "NotBearer x.y.z"},
    )
    assert response.status_code == 401


def test_me_rejects_invalid_bearer_token(api_client: TestClient) -> None:
    response = api_client.get(
        "/api/me",
        headers={"Authorization": "Bearer not-a-real-jwt"},
    )
    assert response.status_code == 401


def test_me_accepts_access_token_cookie(api_client: TestClient) -> None:
    token_response = api_client.post(
        "/api/token",
        data={"username": "testuser", "password": "testpass"},
    )
    token = token_response.json()["access_token"]
    api_client.cookies.set(COOKIE_NAME, token)
    me = api_client.get("/api/me")
    assert me.status_code == 200
    assert me.json() == {"username": "testuser"}


def test_logged_in_users_requires_authentication(api_client: TestClient) -> None:
    response = api_client.get("/api/logged-in-users")
    assert response.status_code == 401


def test_logged_in_users_includes_token_user(api_client: TestClient) -> None:
    token_response = api_client.post(
        "/api/token",
        data={"username": "testuser", "password": "testpass"},
    )
    token = token_response.json()["access_token"]
    response = api_client.get(
        "/api/logged-in-users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == {"users": ["testuser"]}


def test_logged_in_users_deduplicates_multiple_tokens(api_client: TestClient) -> None:
    api_client.post(
        "/api/token",
        data={"username": "testuser", "password": "testpass"},
    )
    second = api_client.post(
        "/api/token",
        data={"username": "testuser", "password": "testpass"},
    ).json()["access_token"]
    response = api_client.get(
        "/api/logged-in-users",
        headers={"Authorization": f"Bearer {second}"},
    )
    assert response.status_code == 200
    assert response.json() == {"users": ["testuser"]}


def test_vouches_require_authentication(api_client: TestClient) -> None:
    create_response = api_client.post("/api/vouches", json={"title": "Hiring panel", "threshold": 2})
    assert create_response.status_code == 401

    list_response = api_client.get("/api/vouches")
    assert list_response.status_code == 401


def test_create_vouch_includes_threshold_title_date_and_creator(api_client: TestClient) -> None:
    token = create_access_token("alice")
    response = api_client.post(
        "/api/vouches",
        json={"title": "Security clearance", "threshold": 3},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["id"]
    assert body["title"] == "Security clearance"
    assert body["threshold"] == 3
    assert body["creator"] == "alice"
    assert body["created_at"]
    assert body["vouchers"] == []


def test_add_voucher_stores_date_user_and_parent_vouch_id(api_client: TestClient) -> None:
    creator_token = create_access_token("alice")
    create_vouch = api_client.post(
        "/api/vouches",
        json={"title": "Repo write access", "threshold": 2},
        headers={"Authorization": f"Bearer {creator_token}"},
    )
    vouch_id = create_vouch.json()["id"]

    voucher_token = create_access_token("bob")
    response = api_client.post(
        f"/api/vouches/{vouch_id}/vouchers",
        headers={"Authorization": f"Bearer {voucher_token}"},
    )
    assert response.status_code == 200
    voucher = response.json()["voucher"]
    assert voucher["created_at"]
    assert voucher["vouched_by"] == "bob"
    assert voucher["parent_vouch_id"] == vouch_id

    list_response = api_client.get(
        "/api/vouches",
        headers={"Authorization": f"Bearer {creator_token}"},
    )
    assert list_response.status_code == 200
    listed_vouches = list_response.json()["vouches"]
    assert len(listed_vouches) == 1
    assert listed_vouches[0]["vouchers"][0]["vouched_by"] == "bob"


def test_add_voucher_rejects_duplicate_and_self_vouches(api_client: TestClient) -> None:
    creator_token = create_access_token("alice")
    create_vouch = api_client.post(
        "/api/vouches",
        json={"title": "Incident response", "threshold": 2},
        headers={"Authorization": f"Bearer {creator_token}"},
    )
    vouch_id = create_vouch.json()["id"]

    self_vouch = api_client.post(
        f"/api/vouches/{vouch_id}/vouchers",
        headers={"Authorization": f"Bearer {creator_token}"},
    )
    assert self_vouch.status_code == 400
    assert self_vouch.json()["detail"] == "Users cannot vouch for themselves"

    voucher_token = create_access_token("bob")
    first_vouch = api_client.post(
        f"/api/vouches/{vouch_id}/vouchers",
        headers={"Authorization": f"Bearer {voucher_token}"},
    )
    assert first_vouch.status_code == 200

    duplicate_vouch = api_client.post(
        f"/api/vouches/{vouch_id}/vouchers",
        headers={"Authorization": f"Bearer {voucher_token}"},
    )
    assert duplicate_vouch.status_code == 409
    assert duplicate_vouch.json()["detail"] == "User already vouched for this vouch"


def test_add_voucher_returns_404_for_unknown_vouch(api_client: TestClient) -> None:
    token = create_access_token("bob")
    response = api_client.post(
        "/api/vouches/does-not-exist/vouchers",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Vouch not found"
