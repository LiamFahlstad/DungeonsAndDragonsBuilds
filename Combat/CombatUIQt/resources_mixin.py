"""The combat window's side of running out of resources (the checks and the
question are Combat/Fight/resources.py): the action economy counted only
during turns, and the question asked through the window's Asker
(Combat/CombatUIQt/window_asker.py)."""

from Combat.Fight.resources import counted_action_lack, go_ahead_anyway
from .state import CombatWindowState


class ResourcesMixin(CombatWindowState):
    """The question asked before using something char has run out of."""

    def _action_lack(self, char: dict, action_type: str | None) -> str | None:
        """counted_action_lack: not between encounters, where there are no
        turns (see _add_action_use)."""
        return counted_action_lack(self.phase, char, action_type)

    def _go_ahead_anyway(self, char: dict, doing: str, lacks: list[str | None]) -> bool:
        """go_ahead_anyway, asked through the window's Asker."""
        return go_ahead_anyway(self.asker, char, doing, lacks)
