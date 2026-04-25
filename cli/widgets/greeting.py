from typing import Any
from textual.widgets import Static
from cli.api import PolychromeAPI

class GreetingWidget(Static):
    """Widget to display a greeting."""
    def __init__(self, username: str, api: PolychromeAPI, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.username = username
        self.api = api

    async def on_mount(self) -> None:
        user = await self.api.get_user(self.username)
        if user is None:
            return
        self.update(f"Hello '{user['nameline']}'. ({user['username']})")