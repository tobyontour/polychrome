from __future__ import annotations

import httpx
from textual import events, on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Footer, Header, Input, Static, TextArea

from api.app.models.commentfile import CommentFile, Post
from cli.api import PolychromeAPI


class DraftActionModal(ModalScreen[str]):
    """Modal shown when a draft submit sentinel is entered."""

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static("Draft finished", id="draft-modal-title"),
            Static("Save, delete, or continue editing this draft?", id="draft-modal-message"),
            Horizontal(
                Button("Save", id="draft-action-save", variant="success"),
                Button("Delete", id="draft-action-delete", variant="error"),
                Button("Edit", id="draft-action-edit", variant="primary"),
                id="draft-modal-actions",
            ),
            id="draft-action-modal",
        )

    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:
        action_by_id = {
            "draft-action-save": "save",
            "draft-action-delete": "delete",
            "draft-action-edit": "edit",
        }
        action = action_by_id.get(event.button.id)
        if action is not None:
            self.dismiss(action)

    def on_key(self, event: events.Key) -> None:
        if event.key == "s":
            event.stop()
            self.dismiss("save")
            return
        if event.key == "d":
            event.stop()
            self.dismiss("delete")
            return
        if event.key in {"e", "escape"}:
            event.stop()
            self.dismiss("edit")


class CommentPostComposeScreen(Screen[Post | None]):
    """Screen for composing a new comment-file post."""

    AUTO_FOCUS = "#post-subject"

    def __init__(self, comment: CommentFile, api: PolychromeAPI) -> None:
        super().__init__(id="comment-post-compose")
        self._comment = comment
        self._api = api
        self._showing_modal = False
        self.title = f"Post to {comment.name}"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Static(self._comment.name, id="compose-comment-name"),
            Static(self._comment.header, id="compose-comment-header"),
            Static("Subject", classes="compose-label"),
            Input(placeholder="Post subject", id="post-subject", max_length=80),
            Static("Draft", classes="compose-label"),
            TextArea("", id="post-draft"),
            Static("Enter a single '.' on its own line to finish the draft.", id="compose-hint"),
            Static("", id="compose-status"),
            id="compose-post-form",
        )
        yield Footer()

    @on(TextArea.Changed, "#post-draft")
    def on_post_draft_changed(self, event: TextArea.Changed) -> None:
        if self._showing_modal:
            return

        text_without_sentinel = self._strip_submit_sentinel(event.text_area.text)
        if text_without_sentinel is None:
            return

        self._showing_modal = True
        if text_without_sentinel != event.text_area.text:
            event.text_area.text = text_without_sentinel
        self.app.push_screen(DraftActionModal(), self._handle_draft_action)

    async def _handle_draft_action(self, action: str) -> None:
        self._showing_modal = False
        if action == "save":
            await self._save_draft()
            return
        if action == "delete":
            self.dismiss(None)
            return
        self.query_one("#post-draft", TextArea).focus()

    async def _save_draft(self) -> None:
        subject = self.query_one("#post-subject", Input).value.strip()
        draft = self.query_one("#post-draft", TextArea).text.strip()

        if not subject:
            self._status("Subject is required.", css_class="error")
            return
        if not draft:
            self._status("Draft content is required.", css_class="error")
            return

        from_line = self._api.username if self._api.username else "Anonymous"
        try:
            created_post = await self._api.create_comment_post(
                self._comment.keypath,
                subject=subject,
                content=draft,
                from_line=from_line,
            )
        except httpx.RequestError as exc:
            self._status(f"Failed to save post: {exc}", css_class="error")
            return
        except httpx.HTTPStatusError as exc:
            self._status(f"Failed to save post ({exc.response.status_code}).", css_class="error")
            return

        if created_post is None:
            self._status("Comment file was not found.", css_class="error")
            return

        self._status("Post saved.", css_class="success")
        self.dismiss(created_post)

    def _status(self, message: str, *, css_class: str | None = None) -> None:
        status_widget = self.query_one("#compose-status", Static)
        status_widget.update(message)
        status_widget.remove_class("success")
        status_widget.remove_class("error")
        if css_class:
            status_widget.add_class(css_class)

    @staticmethod
    def _strip_submit_sentinel(text: str) -> str | None:
        normalized = text.replace("\r\n", "\n")
        lines = normalized.split("\n")

        last_non_empty_index = len(lines) - 1
        while last_non_empty_index >= 0 and lines[last_non_empty_index] == "":
            last_non_empty_index -= 1

        if last_non_empty_index < 0 or lines[last_non_empty_index] != ".":
            return None

        filtered_lines = lines[:last_non_empty_index]
        while filtered_lines and filtered_lines[-1] == "":
            filtered_lines.pop()

        return "\n".join(filtered_lines)
