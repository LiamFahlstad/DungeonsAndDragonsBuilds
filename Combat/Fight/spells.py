"""Casting a spell, Qt-free (Notes/combat-ui-refactor-plan.md, step 5.3,
casting): the slot it spends, who it lands on, the timer it keeps on its
caster and how that counts down. The combat window logs these and gives the
spell's badge and conditions (SpellsMixin)."""

from dataclasses import dataclass
from functools import cache

from Combat.Definitions import Action
from Core.Rules import SECONDS_PER_ROUND
from Model.Content.Feature import FeatureTarget

from .logger import Logger
from .stats import _default_stats, increment_named_stat, spell_slots_used_key


@dataclass(frozen=True)
class SpentSlot:
    level: int
    pact: bool  # a Pact Magic slot, not a spell slot


def spend_slot(
    char: dict, level: int, asked_for_pact: bool = False
) -> SpentSlot | None:
    """Spend one of char's slots of `level`: a Pact Magic slot when asked
    for one, or when char has no spell slot of that level left (so a
    Warlock's slot is spent the same way); counted in its statistics. None
    when there's none to spend."""
    level_left = char.get("spell_slots", {}).get(level, 0)
    pact_left = char.get("pact_slots", {}).get(level, 0)
    pact = asked_for_pact or (level_left <= 0 and pact_left > 0)
    if (pact_left if pact else level_left) <= 0:
        return None
    char["pact_slots" if pact else "spell_slots"][level] -= 1
    stats = char.setdefault("stats", _default_stats())
    stats["spell_slots_used"] = stats.get("spell_slots_used", 0) + 1
    level_key = spell_slots_used_key(level)
    stats[level_key] = stats.get(level_key, 0) + 1
    return SpentSlot(level, pact)


def use_slot(
    logger: Logger, char: dict, level: int, asked_for_pact: bool = False
) -> SpentSlot | None:
    """spend_slot, logged so the party's replay spends it too."""
    spent = spend_slot(char, level, asked_for_pact)
    if spent is None:
        return None
    kind = "Pact Magic slot" if spent.pact else "spell slot"
    logger.log(
        f"{char['name']} uses a Level {level} {kind}",
        character=char["name"],
        action=Action.REMOVE_PACT_SLOT if spent.pact else Action.REMOVE_SPELL_SLOT,
        value=level,
    )
    return spent


def count_spell_cast(caster: dict, name: str):
    """A cast of the spell `name` in caster's statistics."""
    stats = caster.setdefault("stats", _default_stats())
    stats["spells_cast"] = stats.get("spells_cast", 0) + 1
    increment_named_stat(stats, "spells_cast_by_name", name)


def log_spell_cast(
    logger: Logger, caster: dict, name: str, level: int, slot_level: int | None
):
    """Count a cast of the spell `name` (of `level`, using a slot of
    slot_level, if any) in caster's stats, and log it so the party's
    replay counts it too. Cast Spell and the Use / Cast dialog share it."""
    count_spell_cast(caster, name)
    upcast = f" at level {slot_level}" if (slot_level or 0) > level else ""
    logger.log(
        f"{caster['name']} casts {name}{upcast}",
        character=caster["name"],
        action=Action.CAST_SPELL,
        value={"spell_name": name},
    )


def spell_called(name: str):
    """The spell called exactly `name` (as a Cast Spell badge is), or None."""
    return _spells_called().get(name)


@cache
def _spells_called() -> dict:
    from CharacterContent.Spells.SpellFactory import SpellFactory

    spells = sorted(SpellFactory.all_spells(), key=lambda s: (s.level, s.name))
    return {spell.name: spell for spell in spells}


def spell_recipients(spell, source: dict, targets: list[dict]) -> list[dict] | None:
    """Who a cast of `spell` by source lands on: source for a spell on
    itself (SELF, or no target type), the targets picked for an AREA (none
    is fine: the caster keeps its duration and concentration), else the
    targets picked; None when it needs a target and none is picked."""
    if spell.target is None or spell.target == FeatureTarget.SELF:
        return [source]
    if spell.target == FeatureTarget.AREA:
        return list(targets)
    return targets or None


def active_spell_record(
    name: str,
    duration: int,
    concentration: bool,
    applied: list[dict],
    ticks_on: str | None,
) -> dict:
    """The timer a spell with a duration keeps on its caster
    (char["active_spells"]): `applied` is what it put on whom, and it counts
    down as `ticks_on`'s turn starts (the turn it was cast on)."""
    return {
        "name": name,
        "time_left": duration,
        "duration": duration,
        "concentration": concentration,
        "applied": applied,
        "ticks_on": ticks_on,
    }


def ticks_now(
    entry: dict, started: set[str], in_order: set[str], new_round: bool
) -> bool:
    """Whether a spell's timer counts down as the turn passes to `started`
    (`new_round` when that begins a round). It counts on the turn the spell
    was cast on, like a timed condition, so a late caster's spell lasts as
    long as anyone's; at the round's start if that combatant has no turn
    (any more), or for a timer that doesn't say."""
    ticks_on = entry.get("ticks_on")
    if ticks_on in in_order:
        return ticks_on in started
    return ticks_on in started or new_round


def tick(entry: dict) -> bool:
    """A round off the spell's timer; True when that ends it."""
    entry["time_left"] = max(entry["time_left"] - SECONDS_PER_ROUND, 0)
    return entry["time_left"] <= 0
