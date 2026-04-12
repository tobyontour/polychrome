import os

# Config is read at import time; set before loading the app.
os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-key-for-tests-32b!!"
os.environ["AUTH_USERNAME"] = "testuser"
os.environ["AUTH_PASSWORD"] = "testpass"
os.environ["COOKIE_SECURE"] = "false"

import pytest
from fastapi.testclient import TestClient

from api.app.login_tracker import login_tracker
from api.app.main import app
from api.app.vouch_tracker import vouch_tracker


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_login_tracker() -> None:
    login_tracker.clear()
    vouch_tracker.clear()
    yield
    login_tracker.clear()
    vouch_tracker.clear()
