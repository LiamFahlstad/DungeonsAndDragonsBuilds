"""Running out of resources: what a combatant has none left of, and the
question that lets the GM go ahead anyway.

The combat UI counts what each use spends: the Action, Bonus Action or
Reaction this round, a spell slot, a feature's uses, a monster's recharge,
per-day and legendary actions, and Legendary Resistance. When something is
used with one of those gone, nothing refuses it: the GM is asked whether to
go ahead anyway (ResourcesMixin._go_ahead_anyway), as when a feature or a
magic item gives an extra one the UI doesn't know about. Going ahead counts
the use, but never takes a count below zero.

Each check returns what's missing as one line, "<resource>: <why>", or None
when there's enough of it.
"""

from PyQt6.QtWidgets import QMessageBox

from Core.Rules import ACTIONS_PER_TURN

from .effect_options import has_slots, row_uses_most, spell_slot_choices
from .monster_actions import (
    MonsterAction,
    is_spent,
    legendary_actions_left,
    legendary_resistances_left,
)
from .state import CombatWindowState


def action_lack(char: dict, action_type: str | None) -> str | None:
    """char has used up its `action_type` ("Action", "Bonus Action",
    "Reaction") this round."""
    if action_type is None:
        return None
    used = (char.get("action_uses") or {}).get(action_type, 0)
    if used < ACTIONS_PER_TURN:
        return None
    if action_type == "Reaction":
        return "Reaction: already used (it comes back at the start of their turn)"
    return f"{action_type}: already used this turn"


def feature_uses_left(char: dict, name: str) -> int | None:
    """How many uses of char's feature `name` are left, or of its feature row
    `name` that counts its own (row_uses_most: "Misty Step (Fey Touched)"),
    or None for one whose uses aren't counted (or that char doesn't have)."""
    feature = next(
        (f for f in char.get("_feature_objects", []) if f.name == name), None
    )
    sheet = char.get("_stat_block")
    if feature is None or feature.uses is None:
        max_uses = row_uses_most(char, name) if feature is None else None
        if max_uses is None:
            return None
    else:
        max_uses = (
            feature.number_of_uses(sheet)
            if sheet is not None
            else feature.uses.max_uses
        )
    used = (char.get("feature_uses_used") or {}).get(name, 0)
    return max(max_uses - used, 0)


def feature_lack(char: dict, name: str, needed: int = 1) -> str | None:
    """char has fewer than `needed` uses of its feature `name` left (none,
    for one use; Elemental Burst needs 2 of Monk's Focus)."""
    left = feature_uses_left(char, name)
    if left == 0:
        return f"{name}: no uses left"
    if left is not None and left < needed:
        return f"{name}: {left} left, {needed} needed"
    return None


def spell_slot_lack(char: dict, spell_level: int, slot_level: int | None) -> str | None:
    """char casts a spell of spell_level without a slot (slot_level None)
    because it has none of that level or higher left. Choosing no slot while
    one is left (a ritual, an item) lacks nothing, and neither does a cantrip
    or a caster whose slots aren't tracked."""
    if slot_level is not None or spell_level == 0 or not has_slots(char):
        return None
    choices = spell_slot_choices(char, spell_level)
    if any(level is not None for _, level in choices):
        return None
    return f"Spell slots: none of level {spell_level} or higher left"


def monster_action_lack(char: dict, action: MonsterAction) -> str | None:
    """char's stat-block action is spent (a recharge or per-day use), or
    costs more legendary actions than char has left."""
    if action.is_limited and is_spent(char, action):
        return f"{action.name}: spent"
    if action.legendary_cost:
        left = legendary_actions_left(char)
        if left < action.legendary_cost:
            return f"Legendary actions: {left} left, {action.legendary_cost} needed"
    return None


def legendary_resistance_lack(char: dict) -> str | None:
    if legendary_resistances_left(char) <= 0:
        return "Legendary Resistance: none left"
    return None


class ResourcesMixin(CombatWindowState):
    """The question asked before using something char has run out of."""

    def _action_lack(self, char: dict, action_type: str | None) -> str | None:
        """action_lack, while the action economy is counted: not between
        encounters, where there are no turns (see _add_action_use)."""
        if self.phase == "PARTY":
            return None
        return action_lack(char, action_type)

    def _go_ahead_anyway(self, char: dict, doing: str, lacks: list[str | None]) -> bool:
        """Whether to go on with `doing` ("Cast Fireball", "Use Second Wind"):
        yes when char lacks nothing (the Nones in `lacks` are what it has
        enough of), else the GM's answer to a warning listing what's gone.
        No is the default, and says so on the status line."""
        missing = [lack for lack in lacks if lack]
        if not missing:
            return True
        listed = "\n".join(f"•  {lack}" for lack in missing)
        answer = QMessageBox.question(
            self._window,
            "Out of resources",
            f"{char['name']} is out of:\n\n{listed}\n\n{doing} anyway?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            return True
        self._show_status(f"Nothing done: {char['name']} is out of resources.")
        return False
