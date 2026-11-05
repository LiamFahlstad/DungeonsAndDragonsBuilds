"""A player's summons in the combat simulator: the creatures a player's
features create or summon (Feature.summons: a Reanimated Companion, a Drake
Companion), as combatant dicts. The UI side is
Combat/CombatUIQt/summons_mixin.py.

A summon is made when it's summoned (create), not before: its card is built
from its SummonSpec with the choice made for it (a drake's Draconic Essence),
at full Hit Points, named "<owner>'s <spec name>" (numbered when the owner has
several). Its dict holds its owner's character name (SUMMON_OF_KEY), where it
came from (SOURCE_KEY, to find the spec again) and the spec's rules it follows
(lifetime, turn, what 0 Hit Points does), so a saved log replays without the
sheet. A summon has no initiative of its own: it takes its turn right after
its owner's (place_after_owners). How many can be out at once, and what
summoning another does then, is make_room.

One that's out stays out as long as its spec's lifetime says (a Reanimated
Companion until a long rest, a drake until it drops to 0 Hit Points): the next
encounter re-creates it as the last one left it (carried_state, last_seen).

Older logs call the owner key "companion_of" and the choice key
"companion_choice" (upgrade_keys reads them), name a summon
"<owner>'s Companion (<type>)" (old_name) and hold a hidden one for every
companion feature, prepared before anything was summoned: a hidden one isn't
out (is_out). Nothing here imports Qt.
"""

import json
from dataclasses import dataclass

from Combat.EncounterLogs import LogJSONEncoder
from Combat.PlayerCombatant import combatant_from_stat_block
from Model.Character import Character
from Model.Content.Feature import Feature
from Model.Content.Summons import SummonContext, SummonSpec, WhenFull

SUMMON_OF_KEY = "summon_of"
# "feature:<feature name>" (later "spell:<spell name>").
SOURCE_KEY = "summon_source"
# The SummonContext it was made with.
CHOICE_KEY = "summon_choice"
SLOT_KEY = "summon_slot"
# Copied from the SummonSpec (their enum values).
LIFETIME_KEY = "summon_lifetime"
TURN_KEY = "summon_turn"
ON_ZERO_HP_KEY = "summon_on_zero_hp"
# The keys older logs used for SUMMON_OF_KEY and CHOICE_KEY.
OLD_KEYS = {"companion_of": SUMMON_OF_KEY, "companion_choice": CHOICE_KEY}
# What a summon keeps from one encounter to the next.
CARRIED_KEYS = ("hp", "temp_hp", "conditions", "hidden_from_players", CHOICE_KEY)
# The keys a summon's card keeps when its stat block is rebuilt.
_IDENTITY_KEYS = (
    "name",
    "create_name",
    SUMMON_OF_KEY,
    SOURCE_KEY,
    CHOICE_KEY,
    SLOT_KEY,
)


@dataclass(frozen=True)
class SummonOption:
    """One summon a player in the window can have: Add Combatant's "Already
    summoned..." entry for it."""

    label: str  # "Hanna's Drake Companion (Cold)"
    owner: dict  # the player's combatant dict
    feature: Feature
    spec: SummonSpec
    choice: str | None


def upgrade_keys(char: dict) -> dict:
    """`char` (a combatant dict from a log) with the keys older logs used
    renamed to today's, in place."""
    for old, new in OLD_KEYS.items():
        if old in char:
            value = char.pop(old)
            char.setdefault(new, value)
    return char


def owner_name(char: dict) -> str | None:
    """The character name of the player whose summon `char` is, if any."""
    return char.get(SUMMON_OF_KEY, char.get("companion_of"))


def choice_of(char: dict) -> str | None:
    """The choice `char` was summoned with (a drake's Draconic Essence)."""
    return char.get(CHOICE_KEY, char.get("companion_choice"))


def is_out(char: dict) -> bool:
    """Whether the summon `char` is out: shown to the players and standing.
    A hidden one (an older log's, prepared before it was summoned) isn't."""
    return not char.get("hidden_from_players") and char.get("hp", 0) > 0


def feature_source(feature: Feature) -> str:
    """SOURCE_KEY's value for a summon of `feature`."""
    return f"feature:{feature.name}"


def feature_summons(sheet: Character) -> list[tuple[Feature, SummonSpec]]:
    """Each SummonSpec of `sheet`'s features, with its feature."""
    return [
        (feature, spec)
        for feature in sheet.iter_features_with_extensions()
        for spec in feature.summons(sheet)
    ]


def source_for(sheet: Character, summon: dict) -> tuple[Feature, SummonSpec] | None:
    """The feature of `sheet` (the owner's character) that summons `summon`,
    and its SummonSpec: by SOURCE_KEY, or in an older log without it by the
    stat block's type."""
    source = summon.get(SOURCE_KEY)
    found = []
    for feature, spec in feature_summons(sheet):
        if source is not None and feature_source(feature) != source:
            continue
        found.append((feature, spec))
    if source is not None and len(found) == 1:
        return found[0]
    return next(
        (
            (feature, spec)
            for feature, spec in found
            if spec.build(sheet, SummonContext()).combatant_type
            == summon.get("combatant_type")
        ),
        None,
    )


def spec_for(sheet: Character, summon: dict) -> SummonSpec | None:
    """The SummonSpec `summon` (of `sheet`'s character) was made from."""
    found = source_for(sheet, summon)
    return None if found is None else found[1]


def summon_name(owner: str, spec: SummonSpec) -> str:
    """What a summon of `owner`'s is called (before numbering)."""
    return f"{owner}'s {spec.name}"


def old_name(owner: str, combatant_type: str) -> str:
    """What older logs called `owner`'s summon of that type."""
    return f"{owner}'s Companion ({combatant_type})"


def numbered(name: str, taken: set[str]) -> str:
    """`name`, numbered " 2", " 3", ... when it's taken: effects find their
    targets by name."""
    number = 2
    unique = name
    while unique in taken:
        unique = f"{name} {number}"
        number += 1
    return unique


def _card(sheet: Character, spec: SummonSpec, ctx: SummonContext) -> dict:
    """One creature of `spec` as a log stores it: plain dicts, not stat-block
    dataclasses."""
    stat_block = spec.build(sheet, ctx)
    for feature in sheet.iter_features_with_extensions():
        feature.modify_summon(sheet, spec, stat_block, ctx)
    return json.loads(
        json.dumps(combatant_from_stat_block(stat_block), cls=LogJSONEncoder)
    )


def create(
    sheet: Character,
    feature: Feature,
    spec: SummonSpec,
    ctx: SummonContext,
    taken: set[str],
) -> list[dict]:
    """The creatures `feature` of `sheet` summons with `ctx`: spec.count of
    them, out at full Hit Points, each named uniquely among `taken` (the
    names in the fight) and each other."""
    owner = sheet.character_name or ""
    taken = set(taken)
    made = []
    for _ in range(spec.count(sheet, ctx)):
        char = _card(sheet, spec, ctx)
        char["name"] = numbered(summon_name(owner, spec), taken)
        taken.add(char["name"])
        char.pop("hidden_from_players", None)
        char["hp"] = char["max_hp"]
        mark(char, sheet, feature, spec)
        if ctx.choice is not None:
            char[CHOICE_KEY] = ctx.choice
        if ctx.slot_level is not None:
            char[SLOT_KEY] = ctx.slot_level
        made.append(char)
    return made


def mark(char: dict, sheet: Character, feature: Feature, spec: SummonSpec):
    """Mark `char` as `sheet`'s character's summon from `feature`'s `spec`:
    its owner, its source and the spec's rules it follows (and an older
    log's keys as today's)."""
    upgrade_keys(char)
    char[SUMMON_OF_KEY] = sheet.character_name
    char[SOURCE_KEY] = feature_source(feature)
    char[LIFETIME_KEY] = spec.lifetime.value
    char[TURN_KEY] = spec.turn.value
    char[ON_ZERO_HP_KEY] = spec.on_zero_hp.value


def set_stat_block(
    summon: dict, sheet: Character, spec: SummonSpec, choice: str | None
):
    """Rebuild `summon`'s card from `spec` with `choice` (None: the build's
    own), keeping its name, owner, source and state (Hit Points, conditions)."""
    fields = _card(sheet, spec, SummonContext(choice=choice))
    for key, value in fields.items():
        if key not in _IDENTITY_KEYS + ("hp", "temp_hp", "conditions"):
            summon[key] = value
    upgrade_keys(summon)
    if choice is None:
        summon.pop(CHOICE_KEY, None)
    else:
        summon[CHOICE_KEY] = choice


def make_room(existing: list[dict], spec: SummonSpec, new: int) -> list[dict] | None:
    """Room for `new` more summons of `spec` beside `existing` (the ones of
    the same owner and source that are out, oldest first): the ones to
    remove for it ([] when there's room), or None when there's none and the
    spec refuses another (a Reanimated Companion while one is out)."""
    if spec.max_out is None or len(existing) + new <= spec.max_out:
        return []
    if spec.when_full is WhenFull.REFUSED:
        return None
    # The newest of them stay, as many as max_out leaves room for.
    keep = max(spec.max_out - new, 0)
    return existing[: len(existing) - keep]


def carried_state(previous: dict, rested: bool = False) -> dict:
    """What a summon that was `previous` at the end of an earlier encounter
    starts the next one with: its Hit Points and conditions (not ones that
    were ending on a timer or a save, which are fight state), and whether
    it's out. One that died is gone until it's summoned again. `rested`: its
    owner finished a long rest since, and one that lasts past it (its
    SummonSpec's lifetime) is back at full Hit Points with nothing on it."""
    previous = upgrade_keys(dict(previous))
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


def last_seen(
    name: str, logs: list[tuple[dict, bool]], aliases: tuple[str, ...] = ()
) -> tuple[dict, bool] | None:
    """The combatant called `name` (or one of `aliases`, the names older logs
    gave it) as the last of the encounter logs `logs` (in the order they were
    played, each with whether a long rest came after it) that has one left
    it, and that log's long-rest flag."""
    names = {name, *aliases}
    found = None
    for data, rested in logs:
        for char in data.get("combatants", []):
            if char.get("name") in names:
                found = (char, rested)
    return found


def place_after_owners(order: list[dict], summons: list[dict]) -> list[dict]:
    """`order` with each of `summons` right after its owner (after any
    summon of theirs before it), or at the end when its owner isn't in it."""
    order = list(order)
    for summon in summons:
        owner = owner_name(summon)
        at = next(
            (i for i, c in enumerate(order) if c["name"] == owner and c is not summon),
            None,
        )
        if at is None:
            order.append(summon)
            continue
        at += 1
        while at < len(order) and owner_name(order[at]) == owner:
            at += 1
        order.insert(at, summon)
    return order
