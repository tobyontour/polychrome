from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from cli.api import PolychromeAPI

class MenuScreen(Screen):
    """Screen for the main application."""

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        api: PolychromeAPI | None = None,
        keypath: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._api = api
        self._keypath = keypath

    def compose(self) -> ComposeResult:
        """Compose the screen."""
        yield Header()
        yield Static(f"Menu: {self._keypath}", id="menu-title")
        yield Footer()