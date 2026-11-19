"""A stat block's speed, senses and spellcasting text, read into the fields
ExtendedCombatantData keeps them in (Notes/explicit-attributes-plan.md,
Phase 4.1): `speed_swim_ft`, `darkvision_ft`, `spell_save_dc`, ...

This is read where content is written: by generate_monsters.py, once for
the stat block files written before the fields existed, and once as a
saved fight loads, for a monster logged before them
(upgrade_stat_block_keys). The fight itself reads the fields, never this
text. The `senses` and `speed_special_rules` strings stay as they are, for
display."""

from __future__ import annotations

import re
from collections.abc import Iterable

# The speeds the speed text gives (a stat block's Speed, Fly and Climb have
# fields of their own), and whether it hovers.
SPEED_FIELDS = ("speed_swim_ft", "speed_burrow_ft", "hover")
# The senses, each's range in feet, whether its Blindsight is all it sees
# by ("blind beyond this radius"), and its Passive Perception.
SENSE_FIELDS = (
    "darkvision_ft",
    "blindsight_ft",
    "blind_beyond",
    "truesight_ft",
    "tremorsense_ft",
    "passive_perception",
)
# What its Spellcasting says: "spell save DC 15", "+7 to hit with spell
# attacks".
SPELLCASTING_FIELDS = ("spell_save_dc", "spell_attack_bonus")
STAT_BLOCK_FIELDS = SPEED_FIELDS + SENSE_FIELDS + SPELLCASTING_FIELDS
# Each field's value when the text doesn't give it.
DEFAULTS = {
    name: False if name in ("hover", "blind_beyond") else None
    for name in STAT_BLOCK_FIELDS
}

_SPEED = re.compile(r"\b(swim|burrow)\s+(\d+)\s*ft\.?", re.IGNORECASE)
# A Fly or Climb Speed in the text, which the fields above don't take:
# the stat block should give it in speed_fly_ft / speed_climb_ft.
_OTHER_SPEED = re.compile(r"\b(fly|climb)\s+(\d+)\s*ft\.?", re.IGNORECASE)
_HOVER = re.compile(r"\bhover\b", re.IGNORECASE)
_SENSE = re.compile(
    r"\b(Blindsight|Darkvision|Truesight|Tremorsense)\s+(\d+)\s*ft\.?"
    r"(\s*\(blind beyond this radius\))?",
    re.IGNORECASE,
)
_PASSIVE_PERCEPTION = re.compile(r"\bPassive Perception\s+(\d+)", re.IGNORECASE)
_SPELL_SAVE_DC = re.compile(r"spell save DC\s+(\d+)")
_SPELL_ATTACK = re.compile(r"([+-]\d+) to hit with spell attacks")


def read_speed_text(text: str) -> dict:
    """The fields `speed_special_rules` text gives: "burrow 20 ft.; swim 30
    ft." -> {"speed_burrow_ft": 20, "speed_swim_ft": 30}, "hover" ->
    {"hover": True}. Only the ones it gives."""
    found: dict = {}
    for kind, feet in _SPEED.findall(text or ""):
        name = f"speed_{kind.lower()}_ft"
        found[name] = max(found.get(name, 0), int(feet))
    if _HOVER.search(text or ""):
        found["hover"] = True
    return found


def other_speeds_in(text: str) -> list[str]:
    """A Fly or Climb Speed written in the speed text ("fly 30 ft."), which
    belongs in speed_fly_ft / speed_climb_ft instead."""
    return [m[0] for m in _OTHER_SPEED.finditer(text or "")]


def read_senses(text: str) -> dict:
    """The fields `senses` text gives: "Blindsight 30 ft. (blind beyond this
    radius), Darkvision 120 ft., Passive Perception 15" ->
    {"blindsight_ft": 30, "blind_beyond": True, "darkvision_ft": 120,
    "passive_perception": 15}. Only the ones it gives."""
    found: dict = {}
    for match in _SENSE.finditer(text or ""):
        name = f"{match[1].lower()}_ft"
        found[name] = max(found.get(name, 0), int(match[2]))
        if match[3] and name == "blindsight_ft":
            found["blind_beyond"] = True
    passive = _PASSIVE_PERCEPTION.search(text or "")
    if passive:
        found["passive_perception"] = int(passive[1])
    return found


def read_spellcasting(descriptions: Iterable[str]) -> dict:
    """The fields a stat block's actions' and traits' text gives: the first
    "spell save DC 15" and the first "+7 to hit with spell attacks". Only
    the ones it gives; a stat block that states only the DC has no attack
    bonus here (the fight works it out from the DC)."""
    found: dict = {}
    for text in descriptions:
        dc = _SPELL_SAVE_DC.search(text or "")
        if dc and "spell_save_dc" not in found:
            found["spell_save_dc"] = int(dc[1])
        attack = _SPELL_ATTACK.search(text or "")
        if attack and "spell_attack_bonus" not in found:
            found["spell_attack_bonus"] = int(attack[1])
    return found


def _description(ability) -> str:
    if isinstance(ability, dict):
        return ability.get("description", "") or ""
    return getattr(ability, "description", "") or ""


def spellcasting_descriptions(actions, traits) -> list[str]:
    """The texts read_spellcasting reads: actions first, then traits (a
    monster's Spellcasting is an action; an older one's, a trait)."""
    return [_description(a) for a in [*(actions or ()), *(traits or ())]]


def read_stat_block(speed_text: str, senses_text: str, actions=(), traits=()) -> dict:
    """Every field the stat block's text gives, in STAT_BLOCK_FIELDS order:
    only the ones it gives."""
    found = {
        **read_speed_text(speed_text),
        **read_senses(senses_text),
        **read_spellcasting(spellcasting_descriptions(actions, traits)),
    }
    return {name: found[name] for name in STAT_BLOCK_FIELDS if name in found}


def upgrade_stat_block_keys(char: dict) -> dict:
    """A monster's combat dict from a log saved before these fields, with
    them read from its text once, in place. A dict that has them, or isn't
    a stat block's (a player's), is left as it is."""
    if "senses" not in char or any(name in char for name in STAT_BLOCK_FIELDS):
        return char
    read = read_stat_block(
        str(char.get("speed_special_rules") or ""),
        str(char.get("senses") or ""),
        char.get("actions"),
        char.get("traits"),
    )
    char.update({**DEFAULTS, **read})
    return char
