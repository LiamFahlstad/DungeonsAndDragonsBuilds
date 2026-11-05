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
sheet. Most summons have no initiative of their own: they take their turn
right after their owner's (place_after_owners); one whose spec says
SummonTurn.OWN_INITIATIVE (follows_owner is False) rolls its own. How many can
be out at once, and what summoning another does then, is make_room; how a
feature's summon can be paid for now (its SummonSpec's costs), cost_options.

One that's out stays out as long as its spec's lifetime says (a Reanimated
Companion until a long rest, a drake until it drops to 0 Hit Points): the next
encounter re-creates it as the last one left it (carried_state, last_seen).
One that vanishes at 0 Hit Points (vanishes_at_zero_hp: a drake, not a
Reanimated Companion, whose body stays) leaves the fight then. Summoning,
dismissing and vanishing are logged as Action.SUMMON and Action.DISMISS
(summon_event), so one dismissed or vanished in a later encounter isn't
brought back from an earlier one (dismissed).

Older logs call the owner key "companion_of" and the choice key
"companion_choice" (upgrade_keys reads them), name a summon
"<owner>'s Companion (<type>)" (old_name) and hold a hidden one for every
companion feature, prepared before anything was summoned: a hidden one isn't
out (is_out). Nothing here imports Qt.
"""

import json
from dataclasses import dataclass, field

from Combat.Definitions import Action
from Combat.EncounterLogs import LogJSONEncoder
from Combat.PlayerCombatant import combatant_from_stat_block
from Combat.PlayerLog import is_round_key
from Model.Character import Character
from Model.Content.Feature import Feature
from Model.Content.Summons import (
    OnZeroHp,
    SummonContext,
    SummonSpec,
    SummonTurn,
    WhenFull,
)

SUMMON_OF_KEY = "summon_of"
# "feature:<feature name>" (later "spell:<spell name>").
SOURCE_KEY = "summon_source"
# The SummonSpec's name: a source can have several specs.
SPEC_KEY = "summon_spec"
# The SummonContext it was made with.
CHOICE_KEY = "summon_choice"
SLOT_KEY = "summon_slot"
# Copied from the SummonSpec (their enum values).
LIFETIME_KEY = "summon_lifetime"
TURN_KEY = "summon_turn"
ON_ZERO_HP_KEY = "summon_on_zero_hp"
# An Action.DISMISS event's "reason" for one that vanished at 0 Hit Points.
VANISHED_REASON = "0 hp"
# The keys older logs used for SUMMON_OF_KEY and CHOICE_KEY.
OLD_KEYS = {"companion_of": SUMMON_OF_KEY, "companion_choice": CHOICE_KEY}
# What a summon keeps from one encounter to the next.
CARRIED_KEYS = ("hp", "temp_hp", "conditions", "hidden_from_players", CHOICE_KEY)
# The keys of a summon's dict that aren't its card (keep_card): who it is,
# the spec's rules it follows, and its state in a fight.
_NOT_CARD_KEYS = (
    "name",
    "create_name",
    SUMMON_OF_KEY,
    SOURCE_KEY,
    SPEC_KEY,
    CHOICE_KEY,
    SLOT_KEY,
    LIFETIME_KEY,
    TURN_KEY,
    ON_ZERO_HP_KEY,
    "hp",
    "temp_hp",
    "conditions",
    "hidden_from_players",
    "visibility_states",
    "death_saves",
    "death_saves_fail",
    "death_saves_success",
    "spell_slots",
    "stats",
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


@dataclass(frozen=True)
class SummonPayment:
    """One way a player can pay for a feature's summon now (cost_options):
    a use of a feature, a spell slot, or nothing (a free summon)."""

    # The feature whose use is spent, and how many of its uses are left (only
    # what the menu says: not part of which way to pay it is).
    feature_use: str | None = None
    uses_left: int = field(default=0, compare=False)
    # Whether that feature is the one that summons (its own use).
    own_use: bool = False
    # The level of the slot spent; a Pact Magic slot's when `pact`.
    slot_level: int | None = None
    pact: bool = False

    @property
    def text(self) -> str:
        """What the card menu says it costs: "1 use left", "a level 2 slot"."""
        if self.feature_use is not None:
            uses = f"{self.uses_left} use{'' if self.uses_left == 1 else 's'} left"
            return uses if self.own_use else f"a {self.feature_use} use, {uses}"
        if self.slot_level is not None:
            kind = "Pact Magic slot" if self.pact else "slot"
            return f"a level {self.slot_level} {kind}"
        return "free"


def cost_options(
    owner: dict, sheet: Character, feature: Feature, spec: SummonSpec
) -> list[SummonPayment]:
    """The ways `owner` (a player's combatant dict, of the character `sheet`)
    can pay for `feature`'s summon `spec` now, cheapest first: each of
    spec.costs in its order, a slot cost as each level of slot they have left
    from its lowest level up (a spell slot before a Pact Magic slot of the
    same level). [] when they can't pay; a free summon (no costs) costs
    nothing (one SummonPayment with nothing in it)."""
    if not spec.costs:
        return [SummonPayment()]
    used = owner.get("feature_uses_used", {})
    features = {f.name: f for f in sheet.iter_features_with_extensions()}
    features[feature.name] = feature
    options: list[SummonPayment] = []
    for cost in spec.costs:
        found: list[SummonPayment] = []
        if cost.spell_slot is not None:
            minimum = cost.spell_slot
            slots = [
                (int(level), pact)
                for pact, pool in ((False, "spell_slots"), (True, "pact_slots"))
                for level, left in owner.get(pool, {}).items()
                if left > 0 and int(level) >= minimum
            ]
            found = [
                SummonPayment(slot_level=level, pact=pact)
                for level, pact in sorted(slots)
            ]
        else:
            name = cost.feature_use or feature.name
            source = features.get(name)
            left = 0
            if source is not None:
                left = source.number_of_uses(sheet) - used.get(name, 0)
            if left > 0:
                found = [
                    SummonPayment(
                        feature_use=name,
                        uses_left=left,
                        own_use=name == feature.name,
                    )
                ]
        options += [option for option in found if option not in options]
    return options


def follows_owner(char: dict) -> bool:
    """Whether the summon `char` takes its turn right after its owner's
    rather than rolling its own initiative (an older log's always does)."""
    return char.get(TURN_KEY) != SummonTurn.OWN_INITIATIVE.value


def vanishes_at_zero_hp(char: dict) -> bool:
    """Whether the summon `char` leaves the fight when it drops to 0 Hit
    Points (OnZeroHp.VANISHES) rather than staying, dead. Read from its dict,
    so a saved log replays without the sheet; an older log's summon without
    the key stays."""
    return char.get(ON_ZERO_HP_KEY) == OnZeroHp.VANISHES.value


def summon_event(
    summons: list[dict],
    *,
    before_combat: bool = False,
    replaced: bool = False,
    reason: str | None = None,
    initiative: dict[str, int] | None = None,
) -> dict[str, object]:
    """The value of an Action.SUMMON or Action.DISMISS event about `summons`
    (all of one source): where they came from, with which choice and slot
    (SummonContext: for a feature's, the slot that paid for it), and their
    names; "before_combat" for ones that join already summoned,
    "replaced" for ones another summon replaced, the "reason" one left the
    fight on its own ("0 hp": it vanished), and the "initiative" each one
    that rolls its own rolled, by name."""
    first = summons[0] if summons else {}
    value: dict[str, object] = {
        "source": first.get(SOURCE_KEY),
        "choice": choice_of(first),
        "slot": first.get(SLOT_KEY),
        "names": [c["name"] for c in summons],
    }
    if before_combat:
        value["before_combat"] = True
    if replaced:
        value["replaced"] = True
    if reason is not None:
        value["reason"] = reason
    if initiative:
        value["initiative"] = initiative
    return value


def dismissed(data: dict) -> set[str]:
    """The names of the summons the encounter log `data` took out of the
    fight with an Action.DISMISS (dismissed, or replaced by another)."""
    names: set[str] = set()
    for key, events in data.items():
        if not is_round_key(key) or not isinstance(events, list):
            continue
        for event in events:
            if isinstance(event, dict) and event.get("action") == Action.DISMISS:
                value = event.get("value")
                if isinstance(value, dict):
                    names |= set(value.get("names") or [])
    return names


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
    and its SummonSpec: by SOURCE_KEY and SPEC_KEY (a feature can have
    several specs), or in an older log without them by the stat block's
    type."""
    source = summon.get(SOURCE_KEY)
    spec_name = summon.get(SPEC_KEY)
    found = []
    for feature, spec in feature_summons(sheet):
        if source is not None and feature_source(feature) != source:
            continue
        if spec_name is not None and spec.name != spec_name:
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
    char[SPEC_KEY] = spec.name
    char[LIFETIME_KEY] = spec.lifetime.value
    char[TURN_KEY] = spec.turn.value
    char[ON_ZERO_HP_KEY] = spec.on_zero_hp.value


def keep_card(summon: dict, previous: dict):
    """Give `summon` (made or revealed to carry `previous` over, the same
    summon as an earlier log left it) the card `previous` was built with: a
    log keeps a summon's card as it was built, and only summoning it again
    builds it anew from the owner's sheet (an owner may have levelled up
    since). Its name, owner, rules and state stay `summon`'s."""
    previous = upgrade_keys(json.loads(json.dumps(previous, cls=LogJSONEncoder)))
    for key, value in previous.items():
        if key in summon and key not in _NOT_CARD_KEYS:
            summon[key] = value
    for key in (CHOICE_KEY, SLOT_KEY):
        if key in previous:
            summon[key] = previous[key]
        else:
            summon.pop(key, None)


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
    it, and that log's long-rest flag. None when a log after the last that
    has it dismissed it (Action.DISMISS): one taken out of the fight isn't in
    that log's combatants, so an earlier log's would bring it back."""
    names = {name, *aliases}
    found = None
    for data, rested in logs:
        here = None
        for char in data.get("combatants", []):
            if char.get("name") in names:
                here = (char, rested)
        if here is not None:
            found = here
        elif names & dismissed(data):
            found = None
    return found


def place_after_owners(order: list[dict], summons: list[dict]) -> list[dict]:
    """`order` with each of `summons` right after its owner (after any
    summon of theirs before it that goes after them too, not one rolling its
    own initiative), or at the end when its owner isn't in it."""
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
        while (
            at < len(order)
            and owner_name(order[at]) == owner
            and follows_owner(order[at])
        ):
            at += 1
        order.insert(at, summon)
    return order
