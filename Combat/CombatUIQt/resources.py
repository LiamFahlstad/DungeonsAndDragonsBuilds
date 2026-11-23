"""The combat window's side of running out of resources (the checks and the
question are Combat/Fight/resources.py): the action economy counted only
during turns, and the question asked through the window's Asker
(Combat/CombatUIQt/asker.py)."""

from Combat.Definitions import Phase

from Combat.Fight.resources import action_lack, go_ahead_anyway
from .state import CombatWindowState


class ResourcesMixin(CombatWindowState):
    """The question asked before using something char has run out of."""

    def _action_lack(self, char: dict, action_type: str | None) -> str | None:
        """action_lack, while the action economy is counted: not between
        encounters, where there are no turns (see _add_action_use)."""
        if self.phase == Phase.PARTY:
            return None
        return action_lack(char, action_type)

    def _go_ahead_anyway(self, char: dict, doing: str, lacks: list[str | None]) -> bool:
        """go_ahead_anyway, asked through the window's Asker."""
        return go_ahead_anyway(self.asker, char, doing, lacks)
