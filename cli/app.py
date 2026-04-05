"""Textual terminal application for logging into the API."""

from __future__ import annotations

from dataclasses import dataclass

import httpx
from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Static


@dataclass(slots=True)
class LoginResult:
    """Simple authenticated user payload."""

    username: str
    token: str


class ApiLoginApp(App[None]):
    """Terminal UI that authenticates against the API token endpoint."""

    CSS = """
    Screen {
        align: center middle;
    }

    #form {
        width: 70;
        max-width: 90;
        padding: 1 2;
        border: round $accent;
    }

    #title {
        text-style: bold;
        margin-bottom: 1;
    }

    Input {
        margin: 0 0 1 0;
    }

    #actions {
        margin: 0 0 1 0;
        align: right middle;
    }

    #status {
        color: $text-muted;
    }

    #status.success {
        color: $success;
    }

    #status.error {
        color: $error;
    }
    """

    BINDINGS = [("q", "quit", "Quit")]

    _login_result: LoginResult | None = None

    def compose(self) -> ComposeResult:
        """Compose the terminal UI."""
        yield Header()
        with Vertical(id="form"):
            yield Static("Polychrome API Login", id="title")
            yield Input(placeholder="API base URL", value="http://127.0.0.1:8000", id="api-url")
            yield Input(placeholder="Username", id="username")
            yield Input(placeholder="Password", password=True, id="password")
            with Horizontal(id="actions"):
                yield Button("Login", variant="primary", id="login")
            yield Static("Enter credentials and press Login.", id="status")
        yield Footer()

    def _status(self, message: str, *, css_class: str | None = None) -> None:
        status = self.query_one("#status", Static)
        status.update(message)
        status.remove_class("success")
        status.remove_class("error")
        if css_class:
            status.add_class(css_class)

    @on(Button.Pressed, "#login")
    async def on_login_button_pressed(self) -> None:
        await self._login()

    @on(Input.Submitted, "#password")
    async def on_password_submitted(self) -> None:
        await self._login()

    async def _login(self) -> None:
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

        return LoginResult(username=me_payload["username"], token=access_token)


def main() -> None:
    """Run the Textual API login client."""
    ApiLoginApp().run()


if __name__ == "__main__":
    main()
