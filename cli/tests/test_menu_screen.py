import pytest
from cli.app import PolychromeCLIApp
from cli.tests.dummy_api import DummyAPI
from textual.widgets import Button, Static

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
    async with app.run_test():
        assert app.screen.title == "Main Menu"
        assert app.screen.id == "menu--main"
        assert app.screen.query_one("#menu-1", Button).label == "Menu  [1] = Item 1"
        assert app.screen.query_one("#menu-file-3", Button).label == " Add  [3] - Item 3"
        assert app.screen.query_one("#menu-4", Button).label == "Menu  [4] = Item 4"

@pytest.mark.asyncio
async def test_menu_header():
    """Test menu navigation."""
    app = PolychromeCLIApp()
    app._api = DummyAPI(structure_dir="cli/tests/data")
    async with app.run_test():
        assert app.screen.query_one("#menu-header", Static).content == "Header test"

@pytest.mark.asyncio
async def test_menu_navigation():
    """Test menu navigation."""
    app = PolychromeCLIApp()
    app._api = DummyAPI(structure_dir="cli/tests/data")
    async with app.run_test():
        assert app.screen.query_one("#menu-owner", Static).content == "(toby)"
        assert app.screen.query_one("#back", Button).label == "Back"
        assert app.screen.query_one("#scan", Button).label == "Scan"
        assert app.screen.query_one("#options", Button).label == "Options"
        assert app.screen.query_one("#help", Button).label == "Help"

@pytest.mark.asyncio
async def test_greeting():
    """Test menu navigation."""
    app = PolychromeCLIApp()
    app._api = DummyAPI(structure_dir="cli/tests/data")
    async with app.run_test():
        assert app.screen.query_one("#greeting", Static).content == "Hello 'Quick brown fox'. (testuser)"

@pytest.mark.asyncio
async def test_menu_navigation_to_item():
    """Test menu navigation."""
    app = PolychromeCLIApp()
    app._api = DummyAPI(structure_dir="cli/tests/data")
    async with app.run_test() as pilot:
        await pilot.press("1")
        assert pilot.app.screen.title == "Menu 1"
        assert pilot.app.screen.id == "menu-1"
        assert pilot.app.screen.query_one("#menu-header", Static).content == "Menu 1 header"
        assert pilot.app.screen.query_one("#menu-file-5", Button).label == " Add  [5] - Item 5"
