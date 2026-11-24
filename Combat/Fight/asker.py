"""How the fight asks the GM something, Qt-free (Notes/combat-ui-refactor-plan.md,
step 5.4). When a rule needs an answer in the middle of an operation, it
asks through the Asker it was given instead of opening a dialog itself: the
combat window answers with its dialogs (Combat/CombatUIQt/window_asker.py), and a
test answers with a ScriptedAsker.

So far the Asker asks one question: whether to go ahead with something a
combatant has run out of (Combat/Fight/resources.py). The trigger pop-up and
the initiative tie-break join it as the code that asks them moves here."""

from dataclasses import dataclass, field
from typing import Protocol


class Asker(Protocol):
    def go_ahead_anyway(self, char: dict, doing: str, missing: list[str]) -> bool:
        """Whether to go on with `doing` ("Cast Fireball") although char is
        out of each of `missing` (never empty: "Bonus Action: already used
        this turn")."""
        ...


@dataclass
class ScriptedAsker:
    """An Asker that answers from a script, for tests: each go_ahead_anyway
    takes the next of `answers` (or `default` once they run out), and every
    question asked is kept in `asked` as (char's name, doing, missing)."""

    answers: list[bool] = field(default_factory=list)
    default: bool = False
    asked: list[tuple[str, str, list[str]]] = field(default_factory=list)

    def go_ahead_anyway(self, char: dict, doing: str, missing: list[str]) -> bool:
        self.asked.append((char["name"], doing, list(missing)))
        return self.answers.pop(0) if self.answers else self.default
