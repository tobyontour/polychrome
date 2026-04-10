from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

class MenuScreen(Screen):
    """Screen for the main application."""

    def compose(self) -> ComposeResult:
        """Compose the screen."""
        yield Header()
        yield Static("Main screen")
        yield Footer()