"""What a creature can see on the battle map, with no Qt
(Notes/combat-arena-plan.md, step 28; the map painter plan's Q5), from the
Rules Glossary's Vision and Senses:

- Darkness is Heavily Obscured, and "You have the Blinded condition while
  trying to see something in a Heavily Obscured space": a creature every
  cell of which is in such a space isn't seen; one partly out of it is.
  Darkvision sees in Darkness within its range "as if it were Dim Light"
  (seen, then), and Truesight in "normal and magical Darkness".
- A kept area whose text makes it so is the same (`area_obscures`): the
  Darkness spell's "magical Darkness" ("Darkvision can't see through it":
  only Truesight does), Fog Cloud's "The Sphere is Heavily Obscured" (no
  sight sees through a fog).
- Blindsight sees "anything that isn't behind Total Cover" within its range,
  Blinded, in Darkness or Invisible; a stat block's "(blind beyond this
  radius)" sees nothing farther.
- An Invisible creature (Rules Glossary, Invisible) is seen only by
  Blindsight, Truesight or See Invisibility within reach, unless it can't
  benefit from the condition (Faerie Fire). A Blinded viewer sees nothing
  but by Blindsight.

A viewer's senses are its stat block's ("Blindsight 10 ft., Darkvision 60
ft."), a player's sheet's, and its badges' `Vision` (the Darkvision
spell). Tremorsense isn't sight. Whether a creature behind Total Cover is
seen by eyes, and Dim Light (Lightly Obscured: Perception only), are the
GM's: neither changes what's returned. Nothing here does arithmetic on a
cell's coordinates (Decision 3)."""

from __future__ import annotations

import re
from collections.abc import Iterable

from Combat.Arena.arena import ArenaSettings, distance_ft, footprint
from Combat.Arena.cover import cover_from
from Combat.Arena.geometry import Cell
from Combat.Arena.lasting import ACTIVE_SPELLS_KEY, AREA_KEY, record_cells
from Combat.Arena.terrain import DARK as PAINTED_DARK
from Combat.Effects.modifiers import has_condition, modifiers_on
from Combat.Effects.sight import UNKNOWN, Seen
from Core.Definitions import Condition, Sense
from Model.Content.CombatModifiers import Vision

# What a space is to sight, from the least hidden: Darkness (Darkvision and
# Truesight see in it), magical Darkness Darkvision can't see through
# (Truesight only) and a Heavily Obscured fog (no sight but Blindsight).
DARKNESS = "Darkness"
DEEP_DARKNESS = "magical Darkness"
FOG = "Heavily Obscured"
_STRENGTH = (DARKNESS, DEEP_DARKNESS, FOG)

_DARKVISION_CANT = re.compile(r"\bdarkvision can['’]t see through\b", re.IGNORECASE)
_DARKNESS = re.compile(r"\bmagical darkness\b|\bsphere of darkness\b", re.IGNORECASE)
_HEAVILY_OBSCURED = re.compile(r"\bHeavily Obscured\b", re.IGNORECASE)
_SENSE = re.compile(
    r"\b(Blindsight|Darkvision|Truesight|Tremorsense)\s+(\d+)\s*ft\.?"
    r"(\s*\(blind beyond this radius\))?",
    re.IGNORECASE,
)
_SENSES_BY_NAME = {sense.value.lower(): sense for sense in Sense}
_VISION_FIELDS = {
    Sense.DARKVISION: "darkvision_ft",
    Sense.BLINDSIGHT: "blindsight_ft",
    Sense.TRUESIGHT: "truesight_ft",
}


def area_obscures(text: str) -> str | None:
    """What a kept area's rules text makes its space to sight: DEEP_DARKNESS
    (the Darkness spell: "Darkvision can't see through it"), DARKNESS
    ("magical Darkness" otherwise, Hunger of Hadar's "Sphere of Darkness"),
    FOG ("Heavily Obscured": Fog Cloud, Stinking Cloud), or None."""
    if _DARKVISION_CANT.search(text):
        return DEEP_DARKNESS
    if _DARKNESS.search(text):
        return DARKNESS
    if _HEAVILY_OBSCURED.search(text):
        return FOG
    return None


def _stronger(a: str | None, b: str) -> str:
    return b if a is None or _STRENGTH.index(b) > _STRENGTH.index(a) else a


def obscured_cells(
    settings: ArenaSettings, chars: Iterable[dict]
) -> dict[Cell, tuple[str, str]]:
    """Each cell sight can't plainly see into, with what it is and what
    makes it so: (DARKNESS, "Darkness at C4") for painted Darkness, (FOG,
    "Clover's Fog Cloud") for a kept area; the most hiding one where
    several are."""
    shape = settings.distance_rule.shape
    found: dict[Cell, tuple[str, str]] = {
        cell: (DARKNESS, f"Darkness at {shape.cell_name(cell)}")
        for cell, spot in settings.terrain.cells.items()
        if spot.light == PAINTED_DARK
    }
    for char in chars:
        for entry in char.get(ACTIVE_SPELLS_KEY) or []:
            record = entry.get(AREA_KEY)
            if not record:
                continue
            kind = area_obscures(record.get("about") or "")
            if kind is None:
                continue
            what = f"{char['name']}'s {entry['name']}"
            for cell in record_cells(record, char, settings):
                here = found.get(cell)
                if here is None or _stronger(here[0], kind) != here[0]:
                    found[cell] = (kind, what)
    return found


def sense_ranges(char: dict) -> dict[Sense, int]:
    """Char's special senses, each's range in feet: its stat block's senses
    text, a player's sheet's, and what its badges' Vision gives (the
    longest of each counts)."""
    ranges: dict[Sense, int] = {}

    def add(sense: Sense, feet: int):
        ranges[sense] = max(ranges.get(sense, 0), feet)

    for match in _SENSE.finditer(str(char.get("senses") or "")):
        add(_SENSES_BY_NAME[match[1].lower()], int(match[2]))
    sheet_senses = getattr(char.get("_stat_block"), "senses", None)
    if isinstance(sheet_senses, dict):
        for sense, feet in sheet_senses.items():
            if isinstance(sense, Sense) and isinstance(feet, int) and feet > 0:
                add(sense, feet)
    for vision in _visions(char):
        for sense, name in _VISION_FIELDS.items():
            feet = getattr(vision, name)
            if feet:
                add(sense, feet)
    return ranges


def blind_beyond_ft(char: dict) -> int | None:
    """The Blindsight range a stat block says it's "blind beyond", if any."""
    for match in _SENSE.finditer(str(char.get("senses") or "")):
        if match[3] and match[1].lower() == Sense.BLINDSIGHT.value.lower():
            return int(match[2])
    return None


def _visions(char: dict) -> list[Vision]:
    return [m for _, m in modifiers_on(char) if isinstance(m, Vision)]


def sees_invisible(char: dict) -> bool:
    """It sees Invisible creatures as if they were visible (See
    Invisibility)."""
    return any(v.sees_invisible for v in _visions(char))


def outlined(char: dict) -> bool:
    """It can't benefit from the Invisible condition (Faerie Fire)."""
    return any(v.outlined for v in _visions(char))


def _within(ranges: dict[Sense, int], sense: Sense, feet: int) -> bool:
    return ranges.get(sense, 0) >= feet


def _sense_text(ranges: dict[Sense, int], sense: Sense) -> str:
    return f"{sense.value} {ranges[sense]} ft."


def sees(
    viewer: dict, other: dict, chars: Iterable[dict], settings: ArenaSettings
) -> Seen:
    """Whether viewer sees other on the map, and why (module docstring).
    UNKNOWN when either is off it. `settings` is the map as the rules read
    it, kept walls in it (a Wall of Force is Total Cover to Blindsight);
    `chars`, everyone in the fight, for the kept areas and the cover."""
    if viewer is other:
        return Seen(True)
    feet = distance_ft(viewer, other, settings)
    if feet is None:
        return UNKNOWN
    chars = list(chars)
    ranges = sense_ranges(viewer)
    name = other["name"]
    behind = None
    if _within(ranges, Sense.BLINDSIGHT, feet):
        behind = cover_from(viewer, other, chars, settings)
        if not behind.total:
            return Seen(True, _sense_text(ranges, Sense.BLINDSIGHT))
    beyond = blind_beyond_ft(viewer)
    if beyond is not None:  # it has no other sight
        if behind is not None:
            return Seen(False, f"behind Total Cover from {behind.by}")
        return Seen(False, f"blind beyond its Blindsight {beyond} ft.")
    if has_condition(viewer, Condition.BLINDED):
        return Seen(False, f"{viewer['name']} is Blinded")
    truesight = _within(ranges, Sense.TRUESIGHT, feet)
    how = ""
    if has_condition(other, Condition.INVISIBLE) and not outlined(other):
        if truesight:
            how = _sense_text(ranges, Sense.TRUESIGHT)
        elif sees_invisible(viewer):
            how = "See Invisibility"
        else:
            return Seen(False, f"{name} is Invisible")
    return _seen_in_light(viewer, other, chars, settings, ranges, feet, how)


def _seen_in_light(
    viewer: dict,
    other: dict,
    chars: list[dict],
    settings: ArenaSettings,
    ranges: dict[Sense, int],
    feet: int,
    how: str,
) -> Seen:
    """Whether viewer sees other for the spaces other is in: seen when one
    of its cells is lit, or dark to a sense that sees there."""
    cells = footprint(other, settings.distance_rule)
    hidden = obscured_cells(settings, chars)
    darkvision = _within(ranges, Sense.DARKVISION, feet)
    truesight = _within(ranges, Sense.TRUESIGHT, feet)
    through: list[str] = []
    why = ""
    for cell in sorted(cells):
        here = hidden.get(cell)
        if here is None:
            return Seen(True, how)
        kind, what = here
        if kind == DARKNESS and darkvision:
            through.append(_sense_text(ranges, Sense.DARKVISION))
        elif kind in (DARKNESS, DEEP_DARKNESS) and truesight:
            through.append(_sense_text(ranges, Sense.TRUESIGHT))
        elif not why:
            why = what
    if through:
        return Seen(True, how or through[0])
    return Seen(False, why, obscured=True)
