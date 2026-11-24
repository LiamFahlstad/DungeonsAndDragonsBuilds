"""Running out of resources, Qt-free (Notes/combat-ui-refactor-plan.md,
step 5.4): what a combatant has none left of, and asking the GM whether to
go ahead anyway.

The combat UI counts what each use spends: the Action, Bonus Action or
Reaction this round, a spell slot, a feature's uses, a monster's recharge,
per-day and legendary actions, and Legendary Resistance. When something is
used with one of those gone, nothing refuses it: the GM is asked whether to
go ahead anyway (go_ahead_anyway, through the fight's Asker), as when a
feature or a magic item gives an extra one the UI doesn't know about. Going
ahead counts the use, but never takes a count below zero.

Each check returns what's missing as one line, "<resource>: <why>", or None
when there's enough of it.
"""

from Combat.Definitions import Action, ActionCost, Phase
from Core.Rules import ACTIONS_PER_TURN

from .asker import Asker
from .logger import Logger
from .stats import _default_stats, increment_named_stat
from .effect_options import has_slots, row_uses_most, spell_slot_choices
from .monster_actions import (
    MonsterAction,
    is_spent,
    legendary_actions_left,
    legendary_resistances_left,
)


def action_lack(char: dict, action_type: str | None) -> str | None:
    """char has used up its `action_type` ("Action", "Bonus Action",
    "Reaction") this round."""
    if action_type is None:
        return None
    used = (char.get("action_uses") or {}).get(action_type, 0)
    if used < ACTIONS_PER_TURN:
        return None
    if action_type == ActionCost.REACTION:
        return "Reaction: already used (it comes back at the start of their turn)"
    return f"{action_type}: already used this turn"


def counted_action_lack(
    phase: Phase, char: dict, action_type: str | None
) -> str | None:
    """action_lack, while the action economy is counted: not between
    encounters (Phase.PARTY), where there are no turns."""
    if phase == Phase.PARTY:
        return None
    return action_lack(char, action_type)


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


def go_ahead_anyway(
    asker: Asker, char: dict, doing: str, lacks: list[str | None]
) -> bool:
    """Whether to go on with `doing` ("Cast Fireball", "Use Second Wind"):
    yes when char lacks nothing (the Nones in `lacks` are what it has
    enough of), else asker's answer to what's gone."""
    missing = [lack for lack in lacks if lack]
    if not missing:
        return True
    return asker.go_ahead_anyway(char, doing, missing)


# ---- Spending them ----


def use_action(logger: Logger, char: dict, action_type: str):
    """char uses its `action_type` ("Action", "Bonus Action", "Reaction")
    this round: counted until its next turn starts (fight.start_turn), and
    logged."""
    counts = char.setdefault("action_uses", {})
    counts[action_type] = counts.get(action_type, 0) + 1
    logger.log(f"{char['name']} uses {action_type}", character=char["name"])


def count_feature_use(
    logger: Logger, source: dict, name: str, counts_uses: bool, count: int = 1
):
    """Count a use of the feature `name` in source's stats, and `count` of
    its uses if it has any (counts_uses; Elemental Burst spends 2 of Monk's
    Focus), and log it so the party's replay counts it too."""
    stats = source.setdefault("stats", _default_stats())
    stats["features_enabled"] = stats.get("features_enabled", 0) + 1
    increment_named_stat(stats, "features_enabled_by_name", name)
    value: dict = {"feature_name": name}
    text = f"{source['name']} uses {name}"
    if count != 1:
        value["count"] = count
        text += f" ({count} uses)"
    logger.log(
        text,
        character=source["name"],
        action=Action.ENABLE_FEATURE,
        value=value,
    )
    if counts_uses:
        used = source.setdefault("feature_uses_used", {})
        used[name] = used.get(name, 0) + count
