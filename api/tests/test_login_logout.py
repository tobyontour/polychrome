"""HTTP tests for session login (JWT cookie) and logout."""

import pytest
from fastapi.testclient import TestClient

from api.app.auth import COOKIE_NAME


def test_login_page_renders_form(client: TestClient) -> None:
    response = client.get("/login")
    assert response.status_code == 200
    body = response.text.lower()
    assert 'method="post"' in body
    assert "/login" in body
    assert "username" in body and "password" in body


def test_login_failure_redirects_with_error(client: TestClient) -> None:
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "wrong"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    location = response.headers.get("location", "")
    assert "/login" in location
    assert "error" in location


@pytest.mark.parametrize(
    "username,password",
    [("nope", "testpass"), ("testuser", "not-the-password")],
)
def test_login_failure_invalid_credentials(
    client: TestClient,
    username: str,
    password: str,
) -> None:
    response = client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert "error" in response.headers.get("location", "")


def test_login_success_sets_cookie_and_api_me(client: TestClient) -> None:
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "testpass"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers.get("location") in ("/", "http://testserver/")

    me = client.get("/api/me")
    assert me.status_code == 200
    assert me.json() == {"username": "testuser"}


def test_login_when_already_authenticated_redirects_home(client: TestClient) -> None:
    client.post("/login", data={"username": "testuser", "password": "testpass"})
    response = client.get("/login", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers.get("location") in ("/", "http://testserver/")


def test_logout_get_clears_session(client: TestClient) -> None:
    client.post("/login", data={"username": "testuser", "password": "testpass"})
    assert client.get("/api/me").status_code == 200
    token = client.cookies.get(COOKIE_NAME)
    assert token is not None

    response = client.get("/logout")
    assert response.status_code == 200
    assert "logged out" in response.text.lower()

    assert client.get("/api/me").status_code == 401
    tracked = client.get(
        "/api/logged-in-users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert tracked.status_code == 200
    assert tracked.json() == {"users": []}


def test_logout_post_clears_session(client: TestClient) -> None:
    client.post("/login", data={"username": "testuser", "password": "testpass"})
    assert client.get("/api/me").status_code == 200
    token = client.cookies.get(COOKIE_NAME)
    assert token is not None

    response = client.post("/logout", follow_redirects=False)
    assert response.status_code == 303
    assert "/login" in response.headers.get("location", "")

    assert client.get("/api/me").status_code == 401
    tracked = client.get(
        "/api/logged-in-users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert tracked.status_code == 200
    assert tracked.json() == {"users": []}


def test_home_shows_user_when_logged_in(client: TestClient) -> None:
    client.post("/login", data={"username": "testuser", "password": "testpass"})
    response = client.get("/")
    assert response.status_code == 200
    assert "testuser" in response.text
