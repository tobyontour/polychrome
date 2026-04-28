from __future__ import annotations

import httpx
from textual import on
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Static
from textual.containers import Vertical

from cli import LoginResult

class LoginScreen(Screen):
    """Screen for logging in to the API."""
    _login_result: LoginResult | None = None
    _remaining_attempts: int = 3

    AUTO_FOCUS = "#username"
    LOGO = r"""
 ____       _            _
|  _ \ ___ | |_   _  ___| |__  _ __ ___  _ __ ___   ___
| |_) / _ \| | | | |/ __| '_ \| '__/ _ \| '_ ` _ \ / _ \
|  __/ (_) | | |_| | (__| | | | | | (_) | | | | | |  __/
|_|   \___/|_|\__, |\___|_| |_|_|  \___/|_| |_| |_|\___|
              |___/
"""

    def __init__(
        self,
        name: str | None = None,
        id: str | None = "login-screen",
        classes: str | None = None,
        api_url: str | None = None
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._api_url = api_url
        self.title = "Login"

    def compose(self) -> ComposeResult:
        """Compose the screen."""
        yield Header()
        yield Vertical(
            Static(self.LOGO, id="logo", markup=False),
            Input(placeholder="API base URL", value=self._api_url or "http://127.0.0.1:8000", id="api-url"),
            Input(placeholder="Username", id="username", max_length=40),
            Input(placeholder="Password", password=True, id="password", max_length=40),
            Button("Login", variant="primary", id="login"),
            Static("Enter credentials and press Login.", id="status"),
            id="form",
        )
        yield Footer()

    @on(Button.Pressed, "#login")
    async def on_login_button_pressed(self) -> None:
        await self._process_login()

    @on(Input.Submitted, "#password")
    async def on_password_submitted(self) -> None:
        await self._process_login()

    async def _process_login(self) -> None:
        result = await self._login()
        if result:
            self.dismiss(result)
        else:
            self._status("Login failed.", css_class="error")
            self._remaining_attempts -= 1
            if self._remaining_attempts > 0:
                self._status(f"Remaining attempts: {self._remaining_attempts}", css_class="error")
            else:
                self.dismiss(None)

    def _status(self, message: str, *, css_class: str | None = None) -> None:
        status = self.query_one("#status", Static)
        status.update(message)
        status.remove_class("success")
        status.remove_class("error")
        if css_class:
            status.add_class(css_class)

    async def _login(self) -> LoginResult | None:
        login_button = self.query_one("#login", Button)
        api_url = self.query_one("#api-url", Input).value.strip().rstrip("/")
        username = self.query_one("#username", Input).value.strip()
        password = self.query_one("#password", Input).value

        if not api_url:
            self._status("API base URL is required.", css_class="error")
            return
        if not username or not password:
            self._status("Username and password are required.", css_class="error")
            return

        login_button.disabled = True
        self._status("Connecting...")

        try:
            self._login_result = await self._authenticate(api_url, username, password)
        except httpx.RequestError as exc:
            self._status(f"Connection failed: {exc}", css_class="error")
            login_button.disabled = False
            return
        except httpx.HTTPStatusError as exc:
            detail = ""
            try:
                body = exc.response.json()
                if isinstance(body, dict):
                    detail = str(body.get("detail", ""))
            except ValueError:
                detail = exc.response.text
            message = detail or f"Authentication failed ({exc.response.status_code})."
            self._status(message, css_class="error")
            login_button.disabled = False
            return
        except ValueError as exc:
            self._status(str(exc), css_class="error")
            login_button.disabled = False
            return

        self._status(f"Logged in as {self._login_result.username}", css_class="success")
        login_button.disabled = False
        return self._login_result

    async def _authenticate(self, api_url: str, username: str, password: str) -> LoginResult:
        token_url = f"{api_url}/api/token"
        me_url = f"{api_url}/api/me"

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            token_response = await client.post(
                token_url,
                data={"username": username, "password": password},
            )
            token_response.raise_for_status()
            token_payload = token_response.json()
            if not isinstance(token_payload, dict):
                raise ValueError("Unexpected token response payload.")

            access_token = token_payload.get("access_token")
            token_type = str(token_payload.get("token_type", "")).lower()
            if not isinstance(access_token, str) or not access_token:
                raise ValueError("Token response missing access_token.")
            if token_type and token_type != "bearer":
                raise ValueError(f"Unsupported token type: {token_type}")

            me_response = await client.get(
                me_url,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            me_response.raise_for_status()
            me_payload = me_response.json()
            if not isinstance(me_payload, dict) or not isinstance(me_payload.get("username"), str):
                raise ValueError("Unexpected /api/me response payload.")

        return LoginResult(username=me_payload["username"], token=access_token, api_url=api_url)
