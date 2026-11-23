"""The combat window's Asker (Combat/Fight/asker.py): it asks the GM with a
dialog over the window. No is each question's default, and a No says on
the status line why nothing was done."""

from PyQt6.QtWidgets import QMessageBox

from .state import CombatWindowState


class WindowAsker:
    def __init__(self, app: CombatWindowState):
        self._app = app

    def go_ahead_anyway(self, char: dict, doing: str, missing: list[str]) -> bool:
        """A warning listing what char is out of, asking whether to go on
        with `doing` anyway."""
        listed = "\n".join(f"•  {lack}" for lack in missing)
        answer = QMessageBox.question(
            self._app._window,
            "Out of resources",
            f"{char['name']} is out of:\n\n{listed}\n\n{doing} anyway?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            return True
        self._app._show_status(f"Nothing done: {char['name']} is out of resources.")
        return False
