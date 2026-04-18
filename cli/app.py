"""Textual terminal application for logging into the API."""

from __future__ import annotations

import sys
from textual.app import App

from cli import LoginResult
from cli.screens import LoginScreen, MenuScreen

from cli.api import PolychromeAPI
class PolychromeCLIApp(App[None]):
    TITLE = "Polychrome"
    CSS_PATH = "css/main.tcss"

    BINDINGS = [("q", "quit", "Quit")]
    _api: PolychromeAPI | None = None
    async def on_mount(self) -> None:
        """Handle mount event."""

        async def check_logged_in(result: LoginResult | None) -> None:
            if result:
                self._api = PolychromeAPI(result.api_url, result.token)

                menu = await self._api.get_menu("_")
                self.push_screen(MenuScreen(menu=menu, api=self._api))
            else:
                sys.exit(1)

        self.SUB_TITLE = "Login"
        self.push_screen(LoginScreen(), check_logged_in)



def main() -> None:
    """Run the Textual API login client."""
    PolychromeCLIApp().run()


if __name__ == "__main__":
    main()
