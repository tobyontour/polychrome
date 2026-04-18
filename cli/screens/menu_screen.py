from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static
from textual import events
from api.app.models.menu import Menu
from cli.api import PolychromeAPI
from cli.screens.commentfile_screen import CommentFileScreen
class MenuScreen(Screen):
    """Screen for the main application."""

    def __init__(
        self,
        menu: Menu,
        api: PolychromeAPI,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._menu = menu
        self._api = api
        self.available_keys = [item.key for item in self._menu.items if item.item_type not in  ["spacer"]]

    def compose(self) -> ComposeResult:
        """Compose the screen."""
        assert self._menu is not None
        yield Header()
        yield Static(self._menu.title, id="menu-title")
        yield Static(self._menu.header, id="menu-header")
        for i, item in enumerate(self._menu.items):
            if item.item_type == "spacer":
                yield Static("---", id=f"menu-spacer-{i}", classes="spacer")
                continue
            if item.item_type == "comment":
                yield Button(f"[{item.key}] {item.title}", id=f"menu-file-{item.key}", compact=True)
                continue
            if item.item_type == "menu":
                yield Button(f"[{item.key}] {item.title}", id=f"menu-{item.key}", compact=True)
                continue
        yield Footer()

    async def on_key(self, event: events.Key) -> None:
        if event.key not in self.available_keys:
            return

        target_item = next((item for item in self._menu.items if item.key == event.key), None)
        if target_item is None:
            return
        if target_item.item_type == "menu":
            menu = await self._api.get_menu(self._menu.keypath + target_item.key)
            if menu is None:
                return
            new_screen = MenuScreen(menu=menu, api=self._api)
            self.app.switch_screen(new_screen)
            return
        if target_item.item_type == "commentfile":
            if not target_item.keypath:
                target_item.keypath = self._menu.keypath + target_item.key
            comment = await self._api.get_comment_file(target_item.keypath)
            if comment is None:
                return
            new_screen = CommentFileScreen(comment=comment, api=self._api)
            self.app.push_screen(new_screen)
            return
