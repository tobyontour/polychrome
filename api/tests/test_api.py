"""Tests for JSON API routes in api.app.api."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from jose import jwt

from api.app.api import router
from api.app.auth import COOKIE_NAME
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
