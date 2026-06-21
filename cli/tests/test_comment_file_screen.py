import pytest
from cli.app import PolychromeCLIApp
from cli.tests.dummy_api import DummyAPI
from textual.widgets import Button, Static
from cli.screens.commentfile_screen import CommentFileScreen
# @pytest.mark.asyncio
def test_menu_snapshot(snap_compare):
    """Test pressing keys has the desired result."""
    app = PolychromeCLIApp()
    app._api = DummyAPI(structure_dir="cli/tests/data")
    assert snap_compare(app)

@pytest.mark.asyncio
async def test_menu_contents():
    """Test menu navigation."""
    app = PolychromeCLIApp()
    app._api = DummyAPI(structure_dir="cli/tests/data")
    async with app.run_test() as pilot:
        await pilot.press("3")
        assert isinstance(pilot.app.screen, CommentFileScreen)
        assert pilot.app.screen.id == "comment-file-3"
        assert pilot.app.screen.title == "Comment File 3"
        assert pilot.app.screen.query_one("#comment-file-name", Static).content == "Comment File 3"
        assert pilot.app.screen.query_one("#comment-file-header", Static).content == "This is the header of comment file 3"
