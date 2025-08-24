from collections.abc import Callable
from typing import Any

from game_engine.console_ui import clear_screen, show_menu


class MenuHandler:
    def __init__(self, title: str):
        self.title = title
        self.options: list[tuple[str, Callable[[], Any]]] = []

    def add_option(self, text: str, action: Callable[[], Any]) -> "MenuHandler":
        """Fluent interface for adding options."""
        self.options.append((text, action))
        return self

    def show(self) -> None:
        """Display menu and handle user choice."""
        while True:
            clear_screen()
            option_texts = [text for text, _ in self.options]
            choice = show_menu(self.title, option_texts)

            if choice == 0:
                break

            _, action = self.options[choice - 1]
            result = action()

            # Handle special return values if needed
            if result == "exit":
                break
