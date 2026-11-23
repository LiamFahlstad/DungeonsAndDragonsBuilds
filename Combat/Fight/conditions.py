"""A combatant's conditions, Qt-free (Notes/combat-ui-refactor-plan.md,
step 5.3, conditions): gaining or losing one, as the combatant and the
fight's statistics see it. What follows from it (Concentration broken, a
Wild Shape form left, grapples ended, a linked badge taken off with its
conditions) and the log line stay the combat window's
(ConditionsMixin._add_condition_to, _remove_condition_from) until the log
moves."""

from dataclasses import dataclass

from Combat.Arena.arena import DASHES_KEY, GRAPPLER_KEY
from Combat.Effects.active_effects import (
    linked_badges_left_without,
    linked_conditions,
    remove_effect,
)
from Combat.Effects.modifiers import hit_point_maximum, rules_condition
from Core.Definitions import Condition
from Model.Content.RulesConditions import conditions_with
from Model.Content.StandardActions import DASH

from .stats import _default_stats, increment_named_stat

# The conditions that give Incapacitated, which breaks Concentration (and
# ends a Wild Shape form): Paralyzed, Petrified, Stunned, Unconscious too.
_INCAPACITATING = conditions_with(Condition.INCAPACITATED)


def incapacitates(name: str) -> bool:
    """Whether a condition named `name` gives Incapacitated, also under a
    longer custom name ("Stunned by Stunning Strike")."""
    return rules_condition(name) in _INCAPACITATING


def incapacitated_by(char: dict) -> str | None:
    """The first (by name) of char's conditions that gives it Incapacitated
    ("You can't take any action, Bonus Action, or Reaction"), or None."""
    incapacitating = [c for c in char["conditions"] if incapacitates(c)]
    return min(incapacitating) if incapacitating else None


def gain_condition(
    char: dict, cond: str, source: dict | None = None, *, counted: bool = True
) -> bool:
    """char gets `cond` from source. Grappled names its grappler, which the
    battle map drags it along by (arena step 22). Counted in both their
    statistics unless not `counted` (a spell's badge beside the conditions
    it gave: Friends beside Charmed). Returns whether it's new: one char
    has already isn't given again."""
    if cond == Condition.GRAPPLED.value and source is not None and source is not char:
        char[GRAPPLER_KEY] = source["name"]
    if cond in char["conditions"]:
        return False
    char["conditions"].append(cond)
    char.setdefault("stats", _default_stats())
    if counted:
        char["stats"]["conditions_received"] = (
            char["stats"].get("conditions_received", 0) + 1
        )
        increment_named_stat(char["stats"], "conditions_received_by_name", cond)
    if source is not None and counted:
        source.setdefault("stats", _default_stats())
        source["stats"]["conditions_given"] = (
            source["stats"].get("conditions_given", 0) + 1
        )
        increment_named_stat(source["stats"], "conditions_given_by_name", cond)
    return True


@dataclass(frozen=True)
class LostCondition:
    """What losing a condition leaves to follow up on."""

    # char's Hit Point maximum before (Aid's raise goes with its badge).
    maximum_before: int
    # The conditions the lost badge stood for (Friends: Charmed), and the
    # badges left standing for none.
    stands_for: list[str]
    emptied: list[str]


def lose_condition(char: dict, cond: str) -> LostCondition | None:
    """char loses `cond`, with its lasting effect (tooltip, colour, timer,
    repeat save), a Dash's movement and who grappled it. None if char
    doesn't have it."""
    if cond not in char["conditions"]:
        return None
    maximum = hit_point_maximum(char)
    stands_for = linked_conditions(char, cond)
    char["conditions"].remove(cond)
    remove_effect(char, cond)
    if cond == DASH:
        char.pop(DASHES_KEY, None)
    if cond == Condition.GRAPPLED.value:
        char.pop(GRAPPLER_KEY, None)
    emptied = linked_badges_left_without(char, cond)
    return LostCondition(maximum, stands_for, emptied)
