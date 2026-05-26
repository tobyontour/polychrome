from textual import events, on
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

from api.app.models.commentfile import CommentFile, Post
from cli.api import PolychromeAPI
from cli.screens.post_compose_screen import CommentPostComposeScreen


class CommentFileScreen(Screen):
    """Screen for the main application."""

    def __init__(
        self,
        comment: CommentFile,
        api: PolychromeAPI,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id or "commentfile-screen", classes=classes)
        self._comment = comment
        self._api = api
        self.title = comment.name

    def compose(self) -> ComposeResult:
        """Compose the screen."""
        yield Header()
        yield Static(self._comment.name, id="comment-name")
        yield Static(self._comment.header, id="comment-header")
        for i, post in enumerate(self._comment.read(0, 10)):
            yield Static(post.date.strftime("%Y-%m-%d %H:%M:%S"), id=f"comment-post-date-{i}", classes="comment-post-date")
            yield Static(post.from_line, id=f"comment-post-from-line-{i}", classes="comment-post-from-line")
            yield Static(post.subject, id=f"comment-post-subject-{i}", classes="comment-post-subject")
            yield Static(post.content, id=f"comment-post-content-{i}", classes="comment-post-content")
            yield Static(post.author, id=f"comment-post-author-{i}", classes="comment-post-author")
        yield Button("Add Post [a]", id="comment-add-post", compact=True)
        yield Footer()

    async def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            event.stop()
            self.app.pop_screen()
            return
        if event.key == "a":
            event.stop()
            await self._open_compose_screen()

    @on(Button.Pressed, "#comment-add-post")
    async def on_add_post_button_pressed(self) -> None:
        await self._open_compose_screen()

    async def _open_compose_screen(self) -> None:
        async def on_compose_result(result: Post | None) -> None:
            if result is None:
                return
            self._comment.posts.append(result)

        self.app.push_screen(CommentPostComposeScreen(comment=self._comment, api=self._api), on_compose_result)