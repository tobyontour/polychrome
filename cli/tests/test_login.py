from cli.app import PolychromeCLIApp
import pytest
from textual.widgets import Static, Input

# @pytest.mark.asyncio
def test_login_screen_snapshot(snap_compare):
    """Test pressing keys has the desired result."""
    app = PolychromeCLIApp()
    assert snap_compare(app)

@pytest.mark.asyncio
async def test_login_screen_contents():
    app = PolychromeCLIApp()
    async with app.run_test():
        # assert snap_compare("path/to/calculator.py", press=["1", "2", "3"])
        assert app.screen.title == "Login"
        assert app.screen.id == "login-screen"
        assert app.screen.query_one("#logo", Static)
        assert app.screen.query_one("#api-url", Input).value == "http://127.0.0.1:8000"
        assert app.screen.query_one("#username", Input).value == ""
        assert app.screen.query_one("#password", Input).value == ""
