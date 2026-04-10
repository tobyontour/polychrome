"""Textual terminal application for logging into the API."""

from __future__ import annotations

import sys
from textual.app import App

from cli import LoginResult
from cli.screens import LoginScreen, MenuScreen

from cli.api import PolychromeAPI
class PolychromeCLIApp(App[None]):
    TITLE = "Polychrome"
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
    _api: PolychromeAPI | None = None
    def on_mount(self) -> None:
        """Handle mount event."""

        def check_logged_in(result: LoginResult | None) -> None:
            if result:
                self._api = PolychromeAPI(result.api_url, result.token)
                self.push_screen(MenuScreen())
            else:
                sys.exit(1)

        self.SUB_TITLE = "Login"
        self.push_screen(LoginScreen(), check_logged_in)



def main() -> None:
    """Run the Textual API login client."""
    PolychromeCLIApp().run()


if __name__ == "__main__":
    main()
