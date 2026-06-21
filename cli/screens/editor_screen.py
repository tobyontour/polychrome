from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static
from textual.containers import Horizontal, Vertical
from textual import events
from api.app.models.commentfile import CommentFile
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

class EditorScreen(Screen):
    """Screen for editing a comment file."""

    def __init__(
        self,
        comment_file: CommentFile,
        api: PolychromeAPI,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = "editor-screen",
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._comment_file = comment_file
        self._api = api

    def compose(self) -> ComposeResult:
        """Compose the screen."""
        yield Header()
        yield Static(self._comment_file.name, id="comment-file-name")
        yield Static(self._comment_file.header, id="comment-file-header")
        yield Footer()