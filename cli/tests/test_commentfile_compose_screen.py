from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from textual.widgets import Button, Input, Static, TextArea

from cli.app import PolychromeCLIApp
from cli.tests.dummy_api import DummyAPI


@pytest.fixture
def app_with_dummy_data(tmp_path: Path) -> PolychromeCLIApp:
    structure_dir = tmp_path / "data"
    shutil.copytree(Path("cli/tests/data"), structure_dir)
    app = PolychromeCLIApp()
    app._api = DummyAPI(structure_dir=str(structure_dir))
    return app


@pytest.mark.asyncio
async def test_commentfile_post_compose_screen_shows_comment_header(app_with_dummy_data: PolychromeCLIApp) -> None:
    async with app_with_dummy_data.run_test() as pilot:
        await pilot.press("3")
        assert app_with_dummy_data.screen.query_one("#comment-header", Static).content == "Item 3 comment header"

        await pilot.press("a")
        assert app_with_dummy_data.screen.id == "comment-post-compose"
        assert app_with_dummy_data.screen.query_one("#compose-comment-header", Static).content == "Item 3 comment header"


@pytest.mark.asyncio
async def test_commentfile_post_compose_shows_draft_modal_and_saves(app_with_dummy_data: PolychromeCLIApp) -> None:
    async with app_with_dummy_data.run_test() as pilot:
        await pilot.press("3")
        await pilot.press("a")

        compose_screen = app_with_dummy_data.screen
        compose_screen.query_one("#post-subject", Input).value = "Sentinel save"
        draft = compose_screen.query_one("#post-draft", TextArea)
        draft.focus()

        await pilot.press("h", "i", "enter", ".", "enter")
        await pilot.pause()
        assert app_with_dummy_data.screen.query_one("#draft-action-save", Button).label == "Save"

        await pilot.press("s")
        await pilot.pause()
        assert app_with_dummy_data.screen.id == "commentfile-screen"

        comment_file = await app_with_dummy_data._api.get_comment_file("3")
        assert comment_file is not None
        assert any(
            post.subject == "Sentinel save" and post.content == "hi"
            for post in comment_file.posts
        )
