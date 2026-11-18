"""Areas that stay on the battle map, with no Qt (Notes/combat-arena-plan.md,
step 11): Moonbeam's Cylinder, Spirit Guardians' Emanation, Web's Cube,
Grease's square, left where they were aimed for as long as the effect runs.

An area that stays is held by an active spell (the caster's
"active_spells" entry, as the Custom Effect makes one), under its "area"
key, so it ends with that entry: when its time runs out, when concentration
on it ends (a failed save, Incapacitated, a new concentration, the C keys),
or when the GM ends it on the card. Undo and the saved fight state carry it
with the entry, as plain JSON (the plan's Decision 4):

    entry["area"] = {
        "shape": "Cylinder", "size_ft": 5, "width_ft": 5, "from_source": False,
        "aim": [col, row],           # where it was aimed; None for an Emanation
        "cells": [[col, row], ...],  # what it covers, fixed where it was put
        "follows": False,            # True: around its caster, wherever it goes
        "color": "#e67e22",
        "key": "3f9a01c2",           # which area it is, to select it by
        "pick": "Moonbeam",          # what it was picked as, and its rules text
        "about": "A silvery beam of pale light shines down ...",
    }

Clicking an area on the map selects it (step 12): its key says which.

An area acts (step 24): its rules text says when (`area_timing`: as a
creature enters it, as it moves onto one, as a turn starts or ends there),
and each time is an `AreaPrompt`, a turn-column button that opens its
effect again on that creature. Moonbeam and Flaming Sphere can be moved
(`move_rule`: how far, and what it costs); the record keeps its key, time
and concentration, with its "aim" and "cells" set anew. A record also
keeps the "slot_level" it was cast with, for its damage when it acts.

An area that isn't aimed (an Emanation, a Sphere around the source) follows
its caster, worked out from where the caster is now; any other stays on the
cells it covered when it was put down (a Cone or Line aimed from the caster
doesn't swing round as the caster walks on).
"""

from __future__ import annotations

import math
import re
import uuid
from dataclasses import dataclass
from typing import Iterable

from Combat.Arena.arena import ArenaSettings, footprint
from Combat.Arena.areas import AreaOfEffect, AreaShape, area_cells
from Combat.Arena.geometry import Cell

AREA_KEY = "area"
ACTIVE_SPELLS_KEY = "active_spells"
# The area's colour when nobody picked one: the aiming shading's orange.
DEFAULT_AREA_COLOR = "#e67e22"


@dataclass(frozen=True)
class LastingArea:
    """What the map draws for an area that stays: whose it is, what it's
    called, the cells it covers now, its colour, and whether it lasts while
    its caster concentrates."""

    caster: str
    name: str
    cells: frozenset[Cell]
    color: str = DEFAULT_AREA_COLOR
    concentration: bool = False
    key: str = ""  # which area it is (area_key)
    selected: bool = False  # the one clicked on the map: edged brighter

    @property
    def title(self) -> str:
        """ "Clover's Moonbeam"."""
        return f"{self.caster}'s {self.name}"


def area_record(
    area: AreaOfEffect,
    source: dict | None,
    aim: Cell | None,
    settings: ArenaSettings,
    color: str = DEFAULT_AREA_COLOR,
    pick: str = "",
    about: str = "",
) -> dict:
    """The "area" an active spell keeps for `area` aimed at `aim` by
    `source`: its cells now, unless it follows its caster, with a key of
    its own, and what it was picked as and its rules text (`pick`,
    `about`)."""
    follows = not area.is_aimed
    cells = [] if follows else sorted(area_cells(area, source, aim, settings))
    return {
        "shape": area.shape.value,
        "size_ft": area.size_ft,
        "width_ft": area.width_ft,
        "from_source": area.from_source,
        "aim": aim.to_list() if aim is not None and not follows else None,
        "cells": [cell.to_list() for cell in cells],
        "follows": follows,
        "color": color,
        "key": uuid.uuid4().hex[:8],
        "pick": pick,
        "about": about,
    }


def area_key(caster: dict, entry: dict) -> str:
    """Which kept area entry's is: its record's key, or for one kept
    without a key, its caster's and its own name."""
    record = entry.get(AREA_KEY) or {}
    return record.get("key") or f"{caster['name']}/{entry['name']}"


def find_area(chars: Iterable[dict], key: str) -> tuple[dict, dict] | None:
    """The caster and active spell holding the kept area `key`, if it's
    still there."""
    for char in chars:
        for entry in char.get(ACTIVE_SPELLS_KEY) or []:
            if entry.get(AREA_KEY) and area_key(char, entry) == key:
                return char, entry
    return None


def time_left_text(seconds: int | None) -> str:
    """ "8 rounds left", "10 minutes left", "1 hour left"; "" for none."""
    if not seconds or seconds <= 0:
        return ""
    for unit, size in (("hour", 3600), ("minute", 60)):
        if seconds % size == 0:
            count = seconds // size
            return f"{count} {unit}{'' if count == 1 else 's'} left"
    rounds = math.ceil(seconds / 6)
    return f"{rounds} round{'' if rounds == 1 else 's'} left"


def record_area(record: dict) -> AreaOfEffect:
    """The AreaOfEffect a kept record describes."""
    return AreaOfEffect(
        AreaShape(record["shape"]),
        int(record["size_ft"]),
        int(record.get("width_ft", 5)),
        bool(record.get("from_source", False)),
    )


def record_origin(record: dict) -> list[Cell] | None:
    """Where an aimed area spreads from, for the cover against it: the cell
    a point area was aimed at (a Fireball's), or None for one that starts
    at its source (a Cone, an Emanation), whose cover is the source's."""
    if record_area(record).starts_at_source or record.get("aim") is None:
        return None
    return [Cell.of(record["aim"])]


def record_cells(record: dict, caster: dict, settings: ArenaSettings) -> set[Cell]:
    """The cells a kept area covers now: around its caster where the caster
    is (none while it's off the map), or the cells it was put on."""
    if record.get("follows"):
        return area_cells(record_area(record), caster, None, settings)
    return {
        cell
        for cell in (Cell.of(c) for c in record.get("cells", []))
        if settings.on_map(cell)
    }


def lasting_areas(chars: Iterable[dict], settings: ArenaSettings) -> list[LastingArea]:
    """Every area that stays on the map, in the order of `chars` and then
    of their active spells; one that covers nothing now (its caster off the
    map) is left out."""
    found = []
    for char in chars:
        for entry in char.get(ACTIVE_SPELLS_KEY) or []:
            record = entry.get(AREA_KEY)
            if not record:
                continue
            cells = record_cells(record, char, settings)
            if not cells:
                continue
            found.append(
                LastingArea(
                    caster=char["name"],
                    name=entry["name"],
                    cells=frozenset(cells),
                    color=record.get("color") or DEFAULT_AREA_COLOR,
                    concentration=bool(entry.get("concentration")),
                    key=area_key(char, entry),
                )
            )
    return found


def areas_at(cell: Cell, areas: Iterable[LastingArea]) -> list[LastingArea]:
    """The areas that cover `cell`."""
    return [area for area in areas if cell in area.cells]


def areas_holding(
    char: dict, areas: Iterable[LastingArea], settings: ArenaSettings
) -> list[LastingArea]:
    """The areas char stands in: any of its cells in them."""
    own = set(footprint(char, settings.distance_rule))
    return [area for area in areas if own.intersection(area.cells)]


def who_is_in(
    chars: Iterable[dict], settings: ArenaSettings
) -> dict[str, set[tuple[str, str]]]:
    """For each of `chars` on the map, the areas it stands in, by (caster,
    name): what entered() compares from before a move to after it."""
    chars = list(chars)
    areas = lasting_areas(chars, settings)
    return {
        char["name"]: {(a.caster, a.name) for a in areas_holding(char, areas, settings)}
        for char in chars
    }


def entered(
    before: dict[str, set[tuple[str, str]]], after: dict[str, set[tuple[str, str]]]
) -> list[tuple[str, tuple[str, str]]]:
    """Who is in an area now that they weren't in before, as (name,
    (caster, area name)), in `after`'s order: a creature that walked in, or
    one an Emanation moved onto as its caster walked."""
    return [
        (name, key)
        for name, keys in after.items()
        for key in sorted(keys - before.get(name, set()))
    ]


# When a kept area acts on a creature (area_timing): as it enters the area,
# as the area moves onto it (moved, or an Emanation following its caster),
# and as its turn starts or ends there.
ENTERS = "enters"
MOVED_ONTO = "moved onto"
STARTS = "starts"
ENDS = "ends"
# What an area whose text says none of these does: what the reminders said
# before step 24, a creature entering it or starting its turn in it.
DEFAULT_TIMING = frozenset({ENTERS, STARTS})
# What the area is called in a spell's text, after "enters the ...".
_AREA_WORDS = (
    r"(?:spell's |spell’s )?(?:area|cylinder|emanation|sphere|cube|cloud|fog|"
    r"wall|square|line|ring|aura|vortex|mist|smoke|storm|zone|webs?)"
)
_ENTERS = re.compile(
    rf"\benters? (?:the |that |its |this )?{_AREA_WORDS}|\benters? it for the first"
    r" time|\bfirst time on a turn\b",
    re.IGNORECASE,
)
# Moonbeam's "when the spell's area moves into its space", Spirit Guardians'
# "whenever the Emanation enters a creature's space", Flaming Sphere's "If
# you move the sphere into a creature's space".
_MOVED_ONTO = re.compile(
    rf"\b{_AREA_WORDS} (?:moves |enters )(?:in)?(?:to )?(?:a creature's |a creature’s"
    r" |its |their )space|\bmove (?:the|it) \w* ?into a creature's space"
    r"|\bmove (?:the|it) \w* ?into a creature’s space",
    re.IGNORECASE,
)
_STARTS = re.compile(r"\bstarts? (?:its|their) turns?\b", re.IGNORECASE)
_ENDS = re.compile(r"\bends? (?:its|their) turns?\b", re.IGNORECASE)
# How a kept area is moved, in its text: Moonbeam's "take a Magic action on
# later turns to move the Cylinder up to 60 feet", Flaming Sphere's "As a
# Bonus Action, you can move the sphere up to 30 feet".
_MOVE_SENTENCE = re.compile(r"[^.]*\bmove (?:the|it)\b[^.]*", re.IGNORECASE)
_MOVE_FEET = re.compile(r"\bup to (\d+) (?:feet|foot|ft\.?)", re.IGNORECASE)
BONUS_ACTION = "Bonus Action"
ACTION = "Action"


def area_timing(text: str) -> frozenset[str]:
    """When a kept area with rules text `text` acts on a creature: ENTERS,
    MOVED_ONTO, STARTS and ENDS as the text says them (Moonbeam's "when the
    spell's area moves into its space and when it enters the spell's area
    or ends its turn there"), DEFAULT_TIMING for a text that says none (or
    no text). An area that acts on who enters it acts on who it's moved
    onto too, as its record can't tell the two apart at a table."""
    found = set()
    if _ENTERS.search(text):
        found |= {ENTERS, MOVED_ONTO}
    if _MOVED_ONTO.search(text):
        found.add(MOVED_ONTO)
    if _STARTS.search(text):
        found.add(STARTS)
    if _ENDS.search(text):
        found.add(ENDS)
    return frozenset(found) or DEFAULT_TIMING


@dataclass(frozen=True)
class MoveRule:
    """How a kept area is moved, from its text: up to `feet` (None: it
    doesn't say), costing its caster `action` (None: nothing, or the text
    doesn't say)."""

    feet: int | None = None
    action: str | None = None

    @property
    def text(self) -> str:
        """ "up to 60 ft., an Action"; "" when the text says neither."""
        parts = []
        if self.feet is not None:
            parts.append(f"up to {self.feet} ft.")
        if self.action is not None:
            parts.append(f"a{'n' if self.action == ACTION else ''} {self.action}")
        return ", ".join(parts)


def move_rule(text: str) -> MoveRule:
    """How far and at what cost a kept area moves, read from the first
    sentence of `text` that moves it: a Bonus Action (Flaming Sphere) or an
    Action ("a Magic action", Moonbeam), and its "up to N feet"."""
    sentence = _MOVE_SENTENCE.search(text)
    if sentence is None:
        return MoveRule()
    words = sentence.group(0)
    feet = _MOVE_FEET.search(words)
    action = None
    if re.search(r"\bBonus Action\b", words, re.IGNORECASE):
        action = BONUS_ACTION
    elif re.search(r"\baction\b", words, re.IGNORECASE):
        action = ACTION
    return MoveRule(int(feet.group(1)) if feet else None, action)


# What each time an area acts is called on its button.
_WHEN_TEXT = {
    ENTERS: "entered it",
    MOVED_ONTO: "it moved onto them",
    STARTS: "starts its turn in it",
    ENDS: "ended its turn in it",
}


@dataclass(frozen=True)
class AreaPrompt:
    """A kept area acting on `target` (arena step 24): a turn-column button
    that opens the Use / Cast dialog on the area's effect (`pick`) with its
    caster `owner` the source and `target` targeted, spending nothing, as
    its cast was spent already. `key` is the area's (area_key), `area` its
    name, `when` which of ENTERS, MOVED_ONTO, STARTS or ENDS it is."""

    owner: dict
    target: dict
    area: str
    key: str
    when: str
    pick: str = ""

    @property
    def caster(self) -> str:
        """Whose area it is (the prompt's source)."""
        return self.owner["name"]

    @property
    def title(self) -> str:
        """ "Clover's Moonbeam"."""
        return f"{self.caster}'s {self.area}"

    @property
    def prompt(self) -> str:
        """Its button in the turn column: "Clover's Moonbeam on Goblin
        (entered it)"."""
        return f"{self.title} on {self.target['name']} ({_WHEN_TEXT[self.when]})"
