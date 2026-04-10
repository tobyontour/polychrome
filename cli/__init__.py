"""Textual terminal client for the polychrome API."""

from dataclasses import dataclass


@dataclass(slots=True)
class LoginResult:
    """Simple authenticated user payload."""

    username: str
    token: str
    api_url: str