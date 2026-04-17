from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static
from textual import events
from api.app.models.menu import Menu

class MenuScreen(Screen):
    """Screen for the main application."""

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        menu: Menu | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._menu = menu
        if self._menu is None:
            raise ValueError("Menu is required")
        self.available_keys = [item.key for item in self._menu.items if item.item_type == "menu"]

    def compose(self) -> ComposeResult:
        """Compose the screen."""
        assert self._menu is not None
        yield Header()
        yield Static(self._menu.title, id="menu-title")
        yield Static(self._menu.header, id="menu-header")
        for item in self._menu.items:
            if item.item_type == "spacer":
                yield Static("---", id="menu-spacer")
                continue
            if item.item_type == "file":
                yield Static(item.title, id="menu-file")
                continue
            if item.item_type == "menu":
                yield Button(item.title, id=f"menu-{item.key}", compact=True)
                continue
        yield Footer()

    def on_key(self, event: events.Key) -> None:
        if event.key not in self.available_keys:
            return
        self.dismiss(event.key)
