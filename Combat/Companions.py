"""A player's companions in the combat simulator: the creatures a player's
features create or summon (Feature.companion: a Reanimated Companion, a Drake
Companion), as combatant dicts.

Every encounter log starts with the companions of the players taking part
(PlayerCombatant.companions_of, EncounterLogs.prepared_log), hidden from the
players, with their owner's character name under COMPANION_OF_KEY. A
companion has no initiative of its own: it takes its turn right after its
owner's (place_after_owners). Summoning one (summon) makes a new creature of
it: its card rebuilt from the feature with the choice made for it (CHOICE_KEY,
e.g. a drake's Draconic Essence), full Hit Points, and shown to the players.
One that's out stays out as long as its feature says (Feature.companion_rules:
a Reanimated Companion until a long rest, a drake until it drops to 0 Hit
Points): the next encounter starts it as the last one left it
(carried_state). Nothing here imports Qt.
"""

import json

from Combat.EncounterLogs import LogJSONEncoder
from Combat.PlayerCombatant import combatant_from_stat_block
from Model.Character import Character
from Model.Content.Feature import Feature

COMPANION_OF_KEY = "companion_of"
CHOICE_KEY = "companion_choice"
# What a companion keeps from one encounter to the next.
CARRIED_KEYS = ("hp", "temp_hp", "conditions", "hidden_from_players", CHOICE_KEY)
# The keys a companion's card keeps when its stat block is rebuilt.
_IDENTITY_KEYS = ("name", "create_name", COMPANION_OF_KEY)


def owner_name(char: dict) -> str | None:
    """The character name of the player whose companion `char` is, if any."""
    return char.get(COMPANION_OF_KEY)


def companion_feature(sheet: Character, companion: dict) -> Feature | None:
    """The feature of `sheet` (the owner's character) that summons
    `companion`, matched by its stat block's type."""
    for feature in sheet.iter_features_with_extensions():
        stat_block = feature.companion(sheet)
        if (
            stat_block is not None
            and stat_block.combatant_type == companion["combatant_type"]
        ):
            return feature
    return None


def set_stat_block(
    companion: dict, sheet: Character, feature: Feature, choice: str | None
):
    """Rebuild `companion`'s card from `feature` with `choice` (None: the
    build's own), keeping its name, owner and state (Hit Points, conditions)."""
    stat_block = feature.companion(sheet, choice)
    assert stat_block is not None
    # As a log stores it: plain dicts, not stat-block dataclasses.
    fields = json.loads(
        json.dumps(combatant_from_stat_block(stat_block), cls=LogJSONEncoder)
    )
    for key, value in fields.items():
        if key not in _IDENTITY_KEYS + ("hp", "temp_hp", "conditions"):
            companion[key] = value
    if choice is None:
        companion.pop(CHOICE_KEY, None)
    else:
        companion[CHOICE_KEY] = choice


def summon(companion: dict, sheet: Character, feature: Feature, choice: str | None):
    """`companion` summoned anew: its card rebuilt with `choice`, at full Hit
    Points with nothing on it, and shown to the players."""
    set_stat_block(companion, sheet, feature, choice)
    companion["hp"] = companion["max_hp"]
    companion["temp_hp"] = 0
    companion["conditions"] = []
    companion["visibility_states"] = []
    companion["death_saves_fail"] = 0
    companion["death_saves_success"] = 0
    companion.pop("hidden_from_players", None)


def carried_state(previous: dict, rested: bool = False) -> dict:
    """What a companion that was `previous` at the end of an earlier encounter
    starts the next one with: its Hit Points and conditions (not ones that
    were ending on a timer or a save, which are fight state), and whether
    it's out. One that died is gone until it's summoned again. `rested`: its
    owner finished a long rest since, and one that lasts past it
    (CompanionRules) is back at full Hit Points with nothing on it."""
    state = {key: previous[key] for key in CARRIED_KEYS if key in previous}
    state.setdefault("hidden_from_players", False)
    ending = {e.get("name") for e in previous.get("timed_conditions", [])}
    ending |= {e.get("condition") for e in previous.get("repeat_saves", [])}
    if "conditions" in state:
        state["conditions"] = [c for c in state["conditions"] if c not in ending]
    if state.get("hp", 1) <= 0:
        state["hidden_from_players"] = True
    elif rested:
        state.update(hp=previous["max_hp"], temp_hp=0, conditions=[])
    return state


def last_seen(name: str, logs: list[tuple[dict, bool]]) -> tuple[dict, bool] | None:
    """The combatant called `name` as the last of the encounter logs `logs`
    (in the order they were played, each with whether a long rest came after
    it) that has one left it, and that log's long-rest flag."""
    found = None
    for data, rested in logs:
        for char in data.get("combatants", []):
            if char.get("name") == name:
                found = (char, rested)
    return found


def place_after_owners(order: list[dict], companions: list[dict]) -> list[dict]:
    """`order` with each of `companions` right after its owner (after any
    companion of theirs before it), or at the end when its owner isn't in it."""
    order = list(order)
    for companion in companions:
        owner = owner_name(companion)
        at = next(
            (
                i
                for i, c in enumerate(order)
                if c["name"] == owner and c is not companion
            ),
            None,
        )
        if at is None:
            order.append(companion)
            continue
        at += 1
        while at < len(order) and owner_name(order[at]) == owner:
            at += 1
        order.insert(at, companion)
    return order
