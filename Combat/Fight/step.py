"""One of the GM's operations on the fight, Qt-free (Notes/combat-ui-refactor-plan.md,
section 2 and R34): what it's given (the fight, how to log and how to ask
the GM) and what it hands back for the window to show (a StepResult).

The rules change the fight and log as they go. What only the window can do
(redraw a card, set the status line, save the fight state, bring the turn
column and the players' screen up to date) they put in the StepResult
instead, and the window does it once, when the operation is over
(Combat/CombatUIQt/steps.py's run_step)."""

from dataclasses import dataclass, field
from typing import Any

from .asker import Asker
from .fight import Fight
from .logger import Logger


@dataclass
class StepResult:
    """What an operation leaves for the window to show."""

    # Whose cards to redraw, each once (kept by identity: two combatants'
    # dicts can be equal).
    changed: list[dict] = field(default_factory=list)
    # What the status line says, in order. A line logged after one clears
    # it, as the window's _log_event clears the status line.
    status: list[str] = field(default_factory=list)
    # Whether to save the fight state now: something changed after the
    # last line logged saved it (what the players have seen of a creature).
    save: bool = False
    # Whether to bring the turn column, the map and the players' screen up
    # to date (leaving a Wild Shape form changes the turn column's buttons).
    views: bool = False
    # The actions spent, (who, "Action" / "Bonus Action" / "Reaction"): a
    # spent Reaction takes away its Opportunity Attack buttons, and the
    # selected card shows what's left.
    spent: list[tuple[dict, str]] = field(default_factory=list)

    def change(self, char: dict):
        """char's card needs redrawing."""
        if not any(c is char for c in self.changed):
            self.changed.append(char)

    def say(self, text: str):
        self.status.append(text)


@dataclass
class Step:
    """What an operation is given: the fight, the window's (or a test's)
    Logger and Asker, and the StepResult it fills in. A Step is a Logger
    itself, so what's logged through it clears the status said before."""

    fight: Fight
    logger: Logger
    asker: Asker
    result: StepResult = field(default_factory=StepResult)

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
        self.result.status.clear()
        return self.logger.log(
            text,
            note_turn=note_turn,
            character=character,
            action=action,
            value=value,
            public=public,
        )
