"""A stat-block ability's name and text, read into the MonsterAbility fields
the combat UI acts on (Notes/explicit-attributes-plan.md, Phase 4.2): its
`recharge`, `per_day`, `legendary_cost`, `at_turn_start`, `casts`,
`uses_ability` and `moves_first`.

This is read where content is written: by generate_monsters.py, once for
the stat block files written before the fields existed, and once as a
saved fight loads, for an ability logged before them
(monster_actions.upgrade_ability_keys). The fight itself reads the fields,
never this text."""

from __future__ import annotations

import re
from collections.abc import Callable, Collection

from Model.Creatures.MonsterAbilities import MonsterCast

ABILITY_FIELDS = (
    "recharge",
    "per_day",
    "legendary_cost",
    "at_turn_start",
    "casts",
    "uses_ability",
    "moves_first",
)
DEFAULTS = {
    "recharge": None,
    "per_day": None,
    "legendary_cost": 1,
    "at_turn_start": "",
    "casts": (),
    "uses_ability": "",
    "moves_first": False,
}

# In its name: "(Recharge 5-6)", "(2/Day)"; in its name or text: "(Costs 2
# Actions)".
_RECHARGE = re.compile(r"\(Recharge\s+(\d)(?:\D\d)?\)")
_PER_DAY = re.compile(r"\((\d+)/Day")
_LEGENDARY_COST = re.compile(r"\(Costs\s+(\d+)\s+Actions?\)")
_START_OF_TURN = re.compile(r"start of (?:each of )?(?:its|the [\w -]+?'s) turns?")
_SENTENCE = re.compile(r"(?<=[.!?])\s+")
# "The lich casts Fear, using ...", "uses Spellcasting to cast Mind Spike
# (level 3 version).", "casts Cure Wounds (level 2 version), Lesser
# Restoration, or Remove Curse, using ...", "casts Counterspell or Shield in
# response to ...", and the older "casts the Sleep spell, ...". The names
# are checked against the spells there are.
_CASTS = re.compile(
    r"\bcasts? (?:the )?(?P<spells>[A-Z].*?)"
    r"(?=, using|\.(?:\s|$)| in response| on that| on the| on a| at will)"
)
_LIST_ITEM = re.compile(r",? or |, ")
_AT_LEVEL = re.compile(
    r"(?P<name>.+?)(?: spell)?(?: \(level (?P<level>\d+) version\))?"
)
# "casts one of the following spells, ... (spell save DC 12):" and its lists.
_FOLLOWING = re.compile(r"following spells[^:]*:")
_SPELL_LIST = re.compile(r"(?P<often>At will|\d+/Day(?: each)?): (?P<spells>[^.]+)")
# "The dragon makes one Rend attack.", "The mummy uses Dreadful Glare."
_MAKES_ONE = re.compile(r"\bmakes one (?P<name>[A-Z][\w'’ -]*?) attack\b")
_USES = re.compile(r"\buses (?P<name>[A-Z][\w'’ -]*?)(?=[.,]| to | on )")
_MOVES = re.compile(r"\bmoves up to\b")
_NAME_ALONE = re.compile(r"\s*\(.*")

SpellNamed = Callable[[str], "str | None"]


def name_alone(name: str) -> str:
    """An ability's name without its "(Recharge 5-6)" or "(Costs 2
    Actions)"."""
    return _NAME_ALONE.sub("", name)


def read_costs(name: str, description: str) -> dict:
    """recharge and per_day from the name, legendary_cost from the name or
    text. Only the ones it gives (a legendary cost of 1 is the default)."""
    found: dict = {}
    recharge = _RECHARGE.search(name)
    if recharge:
        found["recharge"] = int(recharge.group(1))
    per_day = _PER_DAY.search(name)
    if per_day:
        found["per_day"] = int(per_day.group(1))
    cost = _LEGENDARY_COST.search(f"{name} {description}")
    if cost and int(cost.group(1)) != 1:
        found["legendary_cost"] = int(cost.group(1))
    return found


def read_turn_start(description: str) -> str:
    """The sentence saying what a trait does at the start of the monster's
    turn ("The troll regains 15 Hit Points at the start of each of its
    turns."); "" for none."""
    if not _START_OF_TURN.search(description):
        return ""
    sentences = _SENTENCE.split(description)
    return next(s for s in sentences if _START_OF_TURN.search(s)).strip()


def read_casts(description: str, spell_named: SpellNamed) -> tuple[MonsterCast, ...]:
    """The spells the text casts: named ("casts Fear"), or in a
    Spellcasting list ("At will: Thaumaturgy. 2/Day each: Hold Person,
    Silence."). `spell_named` gives a spell's name as the spell list has it,
    or None for a name that isn't a spell."""
    found = []
    for match in _CASTS.finditer(description):
        for spell, level in _named_spells(match["spells"], spell_named):
            found.append(MonsterCast(spell, level))
    following = _FOLLOWING.search(description)
    if following is not None:
        for match in _SPELL_LIST.finditer(description, following.end()):
            often = match["often"]
            per_day = None if often == "At will" else int(often.split("/")[0])
            for spell, level in _named_spells(match["spells"], spell_named):
                found.append(MonsterCast(spell, level, per_day))
    return tuple(found)


def _named_spells(text: str, spell_named: SpellNamed) -> list[tuple[str, int | None]]:
    """The spells "A (level 2 version), B, or C" names that there are."""
    named = []
    for item in _LIST_ITEM.split(text):
        match = _AT_LEVEL.fullmatch(item.strip())
        if match is None:
            continue
        spell = spell_named(match["name"])
        if spell is not None:
            named.append((spell, int(match["level"]) if match["level"] else None))
    return named


def read_uses(name: str, description: str, names: Collection[str]) -> dict:
    """uses_ability and moves_first: the other ability the text makes or
    uses, if `names` (the monster's other abilities' names, lowercased,
    without their "(Recharge ...)") has it, and whether it moves first."""
    for pattern in (_MAKES_ONE, _USES):
        match = pattern.search(description)
        if match is None:
            continue
        other = match["name"]
        if other.lower() in names and other.lower() != name_alone(name).lower():
            found: dict = {"uses_ability": other}
            if _MOVES.search(description):
                found["moves_first"] = True
            return found
    return {}


def read_ability(
    name: str,
    description: str,
    *,
    spell_named: SpellNamed,
    names: Collection[str] = (),
    has_own_roll: bool = False,
    is_trait: bool = False,
) -> dict:
    """Every field the ability's name and text give, in ABILITY_FIELDS
    order: only the ones it gives. `names` are the monster's abilities the
    picker knows by name (spell_named and names: see read_casts and
    read_uses); an ability with a roll of its own (`has_own_roll`) uses no
    other. Only a trait (`is_trait`) acts at the start of the turn."""
    found = read_costs(name, description)
    if is_trait:
        sentence = read_turn_start(description)
        if sentence:
            found["at_turn_start"] = sentence
    casts = read_casts(description, spell_named)
    if casts:
        found["casts"] = casts
    if not has_own_roll:
        found.update(read_uses(name, description, names))
    return {key: found[key] for key in ABILITY_FIELDS if key in found}


def keyword_source(fields: dict) -> list[str]:
    """`fields` (from read_ability) as the keyword arguments a stat block
    file writes: ['recharge=5', 'casts=(MonsterCast("Fear"),)']."""
    lines = []
    for key in ABILITY_FIELDS:
        if key not in fields:
            continue
        value = fields[key]
        if key == "casts":
            items = [_cast_source(c) for c in value]
            joined = f"{items[0]}," if len(items) == 1 else ", ".join(items)
            lines.append(f"casts=({joined})")
        else:
            lines.append(f"{key}={value!r}")
    return lines


def _cast_source(cast: MonsterCast) -> str:
    args = [repr(cast.spell)]
    if cast.level is not None:
        args.append(f"level={cast.level}")
    if cast.per_day is not None:
        args.append(f"per_day={cast.per_day}")
    return f"MonsterCast({', '.join(args)})"
