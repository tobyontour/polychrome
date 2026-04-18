from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header, Static
from api.app.models.commentfile import CommentFile
from cli.api import PolychromeAPI
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
        super().__init__(name=name, id=id, classes=classes)
        self._comment = comment
        self._api = api

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
        yield Footer()