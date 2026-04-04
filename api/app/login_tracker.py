from __future__ import annotations

from threading import Lock

from jose import JWTError, jwt

from .config import ALGORITHM, SECRET_KEY


class LoginTracker:
    """Tracks active login sessions by token in memory."""

    def __init__(self) -> None:
        self._token_to_user: dict[str, str] = {}
        self._lock = Lock()

    def record_login(self, username: str, token: str) -> None:
        with self._lock:
            self._token_to_user[token] = username

    def record_logout(self, token: str) -> None:
        with self._lock:
            self._token_to_user.pop(token, None)

    def get_logged_in_users(self) -> list[str]:
        self._remove_expired_tokens()
        with self._lock:
            return sorted(set(self._token_to_user.values()))

    def clear(self) -> None:
        with self._lock:
            self._token_to_user.clear()

    def _remove_expired_tokens(self) -> None:
        with self._lock:
            for token in list(self._token_to_user.keys()):
                if self._is_token_expired(token):
                    self._token_to_user.pop(token, None)

    @staticmethod
    def _is_token_expired(token: str) -> bool:
        try:
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            return True
        return False


login_tracker = LoginTracker()
