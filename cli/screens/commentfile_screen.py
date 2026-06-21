from textual.app import ComposeResult
from textual.screen import Screen
from textual import events
from textual.widgets import Footer, Header, Static
from textual.binding import Binding
from api.app.models.commentfile import CommentFile
from cli.api import PolychromeAPI
from cli.screens.compose_message_screen import ComposeMessageScreen
from cli.screens.compose_post_screen import ComposePostScreen

class CommentFileScreen(Screen):
    """Screen for the main application."""

    BINDINGS = [
        Binding(key="q,enter", action="exit", description="Exit"),
        Binding(key="s", action="send_reply", description="Send reply"),
        Binding(key="a", action="add", description="Add"),
        Binding(key=".", action="edit", description="Edit"),
        Binding(key="?", action="help", description="Show help screen"),
    ]
    #  [-]:Up  [Q]/[RET]:Exit  [S]:Send Reply  [A]:Add  [.]:Edit  [?]:Help  (100%)

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

    def compose(self) -> ComposeResult:
        """Compose the screen."""
        self.title = self._comment.name
        self.id = f"comment-file-{self._comment.keypath}" if self._comment.keypath != "_" else "comment-file--main"

        yield Header()
        yield Static(self._comment.name, id="comment-file-name")
        yield Static(self._comment.header, id="comment-file-header")
        for i, post in enumerate(self._comment.read(0, 10)):
            yield Static(
                post.date.strftime("%Y-%m-%d %H:%M:%S"), id=f"comment-post-date-{i}", classes="comment-post-date"
            )
            yield Static(f"From: {post.from_line} ({post.author})", id=f"comment-post-from-line-{i}", classes="comment-post-from-line")
            yield Static(post.subject, id=f"comment-post-subject-{i}", classes="comment-post-subject")
            yield Static(post.content, id=f"comment-post-content-{i}", classes="comment-post-content")
        yield Footer()

    async def action_exit(self) -> None:
        self.app.pop_screen()

    async def action_send_reply(self) -> None:
        self.app.push_screen(ComposeMessageScreen(api=self._api, to_user=self._comment.owner))

    async def action_add(self) -> None:
        self.app.push_screen(ComposePostScreen(comment=self._comment, api=self._api))

    # async def action_edit(self) -> None:
    #     self.app.push_screen(EditPostScreen(comment=self._comment, api=self._api))

    # async def action_help(self) -> None:
    #     self.app.push_screen(HelpScreen(comment=self._comment, api=self._api))

    # def on_key(self, event: events.Key) -> None:
    #     if event.key == "enter":
    #         event.stop()
    #         self.app.pop_screen()
