"""The combat window's Logger (Combat/Fight/logger.py): each line the fight's
rules log goes to LoggingMixin._log_event, which appends it to the encounter
log (or a short rest's entry) with whose turn it is, records it in the open
Undo step and works out whether players may read it."""

from typing import Any

from .state import CombatWindowState


class WindowLogger:
    def __init__(self, app: CombatWindowState):
        self._app = app

    def log(
        self,
        text: str,
        *,
        note_turn: bool = True,
        character: str | None = None,
        action: str | None = None,
        value: Any = None,
        public: bool = True,
    ) -> bool:
        return self._app._log_event(
            text,
            note_turn=note_turn,
            character=character,
            action=action,
            value=value,
            public=public,
        )
