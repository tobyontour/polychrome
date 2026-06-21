from textual.screen import Screen
from textual.widgets import Footer, Header, Static
from textual.containers import Vertical
from textual.binding import Binding
from api.app.models.commentfile import CommentFile
from cli.api import PolychromeAPI

class ComposePostScreen(Screen):
    """Screen for composing a post."""

    BINDINGS = [
        Binding(key="f1", action="options", description="Options"),
        Binding(key="f2", action="finish", description="Finish"),
    ]

    def __init__(
        self,
        comment: CommentFile,
        api: PolychromeAPI,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._comment = comment
        self._api = api