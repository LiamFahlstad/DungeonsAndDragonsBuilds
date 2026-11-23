"""A short rest, Qt-free (Notes/combat-ui-refactor-plan.md, step 5.3,
rests): the feature uses and Pact Magic slots a player regains, and the Hit
Points their Hit Dice give back. A long rest needs none of this: it's a line
in the player log, and the party is replayed from after it onto rested
sheets (Combat/PlayerLog.py). The short-rest window logs each regain and
asks for the heals (Combat/CombatUIQt/rest.py)."""

from Combat.PlayerCombatant import max_pact_slots
from Model.Content.Feature import RegainedOn

from .health import DEAD, Regained, death_state, regain_hit_points

SHORT_REST_CADENCES = {RegainedOn.SHORT_REST, RegainedOn.SHORT_OR_LONG_REST}


def regain_feature_uses(char: dict, cadences: set, rest: str) -> list[str]:
    """char regains the spent uses of each feature that comes back on a
    rest of `cadences` (`rest` names it: "short rest"); a feature that gets
    only some back then gets those (Wild Shape, Channel Divinity: "regain
    one expended use"). Returns a feature's name for each use regained, in
    order."""
    stat_block = char.get("_stat_block")
    if stat_block is None:
        return []
    used = char.setdefault("feature_uses_used", {})
    regained_uses: list[str] = []
    for feature in char.get("_feature_objects", []):
        if feature.uses is None:
            continue
        if feature.regained_on(stat_block) not in cadences:
            continue
        regained = used.get(feature.name, 0)
        # Some regain only a few uses on a Short Rest and the rest on a Long
        # one (Wild Shape, Channel Divinity: "regain one expended use").
        partial = feature.uses.regain_x_on
        if partial is not None and partial[1] == rest:
            regained = min(regained, partial[0])
        for _ in range(regained):
            used[feature.name] = max(used.get(feature.name, 0) - 1, 0)
            regained_uses.append(feature.name)
    return regained_uses


def regain_pact_slots(char: dict) -> list[int]:
    """char regains every Pact Magic slot it has spent. Returns the level of
    each slot regained, in order."""
    pact_slots = char.setdefault("pact_slots", {})
    levels: list[int] = []
    for level, most in max_pact_slots(char).items():
        while pact_slots.get(level, 0) < most:
            pact_slots[level] = pact_slots.get(level, 0) + 1
            levels.append(level)
    return levels


def heal_with_hit_dice(char: dict, heal: int) -> Regained | None:
    """char regains `heal` Hit Points from Hit Dice spent on a short rest,
    outside any fight, so not in its statistics. None for a dead creature:
    it regains none until it's revived."""
    if death_state(char) == DEAD:
        return None
    return regain_hit_points(char, heal, None, counted=False)
