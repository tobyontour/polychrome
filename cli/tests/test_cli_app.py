"""Tests for the Textual API login client."""

from __future__ import annotations

import asyncio

import httpx
import pytest

from cli.screens.login_screen import LoginScreen

class FakeAsyncClient:
    """Small async client shim for deterministic HTTP responses."""

    def __init__(self, token_response: httpx.Response, me_response: httpx.Response):
        self._token_response = token_response
        self._me_response = me_response
        self.post_url: str | None = None
        self.post_data: dict[str, str] | None = None
        self.get_url: str | None = None
        self.get_headers: dict[str, str] | None = None

    async def __aenter__(self) -> "FakeAsyncClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:  # type: ignore[override]
        return False

    async def post(self, url: str, data: dict[str, str]) -> httpx.Response:
        self.post_url = url
        self.post_data = data
        return self._token_response

    async def get(self, url: str, headers: dict[str, str]) -> httpx.Response:
        self.get_url = url
        self.get_headers = headers
        return self._me_response


def _response(method: str, url: str, status_code: int, payload: dict[str, str]) -> httpx.Response:
    return httpx.Response(
        status_code,
        request=httpx.Request(method, url),
        json=payload,
    )


def test_authenticate_success(monkeypatch: pytest.MonkeyPatch) -> None:
    token_response = _response(
        "POST",
        "http://example.local/api/token",
        200,
        {"access_token": "token-123", "token_type": "bearer"},
    )
    me_response = _response(
        "GET",
        "http://example.local/api/me",
        200,
        {"username": "testuser"},
    )
    fake_client = FakeAsyncClient(token_response, me_response)
    monkeypatch.setattr("httpx.AsyncClient", lambda **_: fake_client)

    login_screen = LoginScreen()
    result = asyncio.run(login_screen._authenticate("http://example.local", "testuser", "testpass"))

    assert result.username == "testuser"
    assert result.token == "token-123"
    assert fake_client.post_url == "http://example.local/api/token"
    assert fake_client.post_data == {"username": "testuser", "password": "testpass"}
    assert fake_client.get_url == "http://example.local/api/me"
    assert fake_client.get_headers == {"Authorization": "Bearer token-123"}


def test_authenticate_rejects_non_bearer(monkeypatch: pytest.MonkeyPatch) -> None:
    token_response = _response(
        "POST",
        "http://example.local/api/token",
        200,
        {"access_token": "token-123", "token_type": "mac"},
    )
    me_response = _response(
        "GET",
        "http://example.local/api/me",
        200,
        {"username": "testuser"},
    )
    fake_client = FakeAsyncClient(token_response, me_response)
    monkeypatch.setattr("httpx.AsyncClient", lambda **_: fake_client)

    login_screen = LoginScreen()
    with pytest.raises(ValueError, match="Unsupported token type"):
        asyncio.run(login_screen._authenticate("http://example.local", "testuser", "testpass"))


def test_authenticate_rejects_missing_username_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    token_response = _response(
        "POST",
        "http://example.local/api/token",
        200,
        {"access_token": "token-123", "token_type": "bearer"},
    )
    me_response = _response(
        "GET",
        "http://example.local/api/me",
        200,
        {"name": "testuser"},
    )
    fake_client = FakeAsyncClient(token_response, me_response)
    monkeypatch.setattr("httpx.AsyncClient", lambda **_: fake_client)

    login_screen = LoginScreen()
    with pytest.raises(ValueError, match="Unexpected /api/me response payload"):
        asyncio.run(login_screen._authenticate("http://example.local", "testuser", "testpass"))
