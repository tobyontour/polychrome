from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static
from textual.containers import Horizontal, Vertical
from textual import events
from api.app.models.menu import Menu, MenuItem
from cli.api import PolychromeAPI
from cli.screens.commentfile_screen import CommentFileScreen
from cli.widgets.greeting import GreetingWidget

_HORIZONTAL_LINE_CHARS: dict[str, str] = {
    "ascii": "-",
    "blank": " ",
    "dashed": "╍",
    "double": "═",
    "heavy": "━",
    "hidden": " ",
    "none": " ",
    "solid": "─",
    "thick": "█",
}

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
        self.title = self._menu.title
        self.id = f"menu-{self._menu.keypath}" if self._menu.keypath != "_" else "menu--main"
        yield Header()
        yield Horizontal(
            Static(self._menu.title, id="menu-title"),
        )

        with Horizontal():
            with Vertical(id="content"):
                yield Static(self._menu.header, id="menu-header")
                with Horizontal():
                    # width = self.size.width - 20
                    # yield Static(_HORIZONTAL_LINE_CHARS["solid"] * width, id="sidebar-horizontal-rule")
                    yield Static(f"({self._menu.owner})", id="menu-owner")

                for i, item in enumerate(self._menu.items):
                    if item.item_type == "commentfile":
                        yield Button(f" Add  [{item.key}] - {item.title}", id=f"menu-file-{item.key}", compact=True, name=item.key)
                        continue
                    if item.item_type == "menu":
                        yield Button(f"Menu  [{item.key}] = {item.title}", id=f"menu-{item.key}", compact=True, name=item.key)
                        continue
                if self._menu.keypath == "_":
                    assert self._api.username is not None
                    yield GreetingWidget(username=self._api.username, api=self._api, id="greeting")
            # with Vertical(id="sidebar"):
            #     yield Static("Users online:", id="users-online-title")
        with Horizontal():
            yield Button("Back", id="back", compact=True)
            yield Button("Scan", id="scan", compact=True)
            yield Button("Options", id="options", compact=True)
            yield Button("Help", id="help", compact=True)
        yield Footer()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle all button pressed events."""
        if event.button.name:
            print(f"Button pressed: {event.button.name}")
            target_item = next((item for item in self._menu.items if item.key == event.button.name), None)
            if target_item is None:
                print(f"Target item not found: {event.button.name}")
                return
            await self.navigate_to_item(target_item)

    async def navigate_to_item(self, target_item: MenuItem) -> None:
        if target_item.item_type == "menu" and target_item.keypath:
            menu = await self._api.get_menu(target_item.keypath)
            print(f"Navigating to menu: {target_item.keypath}")
            if menu is None:
                return
            new_screen = MenuScreen(menu=menu, api=self._api)
            self.app.switch_screen(new_screen)
            print(f"Switched to menu screen: {target_item.keypath}")
            return
        if target_item.item_type == "commentfile" and target_item.keypath:
            comment = await self._api.get_comment_file(target_item.keypath)
            print(f"Navigating to comment file: {target_item.keypath}")
            if comment is None:
                return
            new_screen = CommentFileScreen(comment=comment, api=self._api)
            self.app.push_screen(new_screen)
            print(f"Pushed comment file screen: {target_item.keypath}")
            return

    # def on_resize(self, event: events.Resize) -> None:
    #     if event.size.width >= 100:
    #         self.query_one("#sidebar").display = "block"
    #     else:
    #         self.query_one("#sidebar").display = "none"

    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            event.stop()
            # Go back to the previous screen
            if self._menu.keypath == "_":
                return
            new_keypath = self._menu.keypath[:-1]
            if new_keypath == "":
                new_keypath = "_"
            menu = await self._api.get_menu(new_keypath)
            if menu is None:
                return
            new_screen = MenuScreen(menu=menu, api=self._api)
            self.app.push_screen(new_screen)
            print(f"Pushed menu screen: {new_keypath}")
            return
        if event.key not in self.available_keys:
            return

        target_item = next((item for item in self._menu.items if item.key == event.key), None)
        if target_item is None:
            return
        await self.navigate_to_item(target_item)
