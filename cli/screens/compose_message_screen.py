from textual.screen import Screen
from textual.widgets import Footer, Header, Static
from textual.containers import Vertical
from textual.binding import Binding
from api.app.models.commentfile import CommentFile
from cli.api import PolychromeAPI
from api.app.models.user import User

class ComposeMessageScreen(Screen):
    """Screen for composing a message."""

    BINDINGS = [
        Binding(key="f1", action="options", description="Options (or [^O])"),
        Binding(key="f2", action="finish", description="Finish"),
        Binding(key="f3", action="mark_block", description="Mark block (or [^B])"),
        Binding(key="f6", action="goto", description="Goto (or [^G])"),
        Binding(key="f7", action="find", description="Find (or [^F])"),
    ]

    #            [F1]:Options (or [^O])       [F3]:Mark Block     [F6]:Goto
    #            [F2]:Finish                                      [F7]:Find

    def __init__(
        self,
        api: PolychromeAPI,
        to_user: User | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        reply_text: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._to_user = to_user
        self._reply_text = reply_text
        self._api = api