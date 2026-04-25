"""Textual terminal application for logging into the API."""

from __future__ import annotations

import sys

from textual.app import App

from cli import LoginResult
from cli.api import PolychromeAPI
from cli.screens import LoginScreen, MenuScreen
from cli.tests.dummy_api import DummyAPI


class PolychromeCLIApp(App[None]):
    TITLE = "Polychrome"
    CSS_PATH = "css/main.tcss"

    BINDINGS = [("q", "quit", "Quit")]
    _api: PolychromeAPI | None = None
    async def on_mount(self) -> None:
        """Handle mount event."""

        if self._api is None:
            async def check_logged_in(result: LoginResult | None) -> None:
                if result:
                    self._api = PolychromeAPI(result.api_url, result.token)

                    menu = await self._api.get_menu("_")
                    if menu is None:
                        raise ValueError("Menu not found")
                    self.push_screen(MenuScreen(menu=menu, api=self._api))
                else:
                    sys.exit(1)

            self.SUB_TITLE = "Login"
            self.push_screen(LoginScreen(), check_logged_in)

        else:
            menu = await self._api.get_menu("_")
            if menu is None:
                raise ValueError("Menu not found")
            self.push_screen(MenuScreen(menu=menu, api=self._api))

def main() -> None:
    """Run the Textual API login client."""
    app = PolychromeCLIApp()
    app._api = DummyAPI(structure_dir="cli/tests/data")
    app.run()


if __name__ == "__main__":
    main()
