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
        "rules": {"shape": "Cylinder", "size_ft": 5, "acts": [...], ...},
    }

Clicking an area on the map selects it (step 12): its key says which.

What the area does while it lasts is its pick's CombatArea
(Model/Content/CombatArea.py), kept as "rules" (None for a pick without
one): never read from "about", which is only shown. A record kept before
2026-11-19 has no "rules"; record_rules takes them from the spell it was
picked as.

An area acts (step 24): its rules say when (`record_timing`: as a creature
enters it, as it moves onto one, as a turn starts or ends there), and each
time is an `AreaPrompt`, a turn-column button that opens its effect again
on that creature. Moonbeam and Flaming Sphere can be moved (`record_move`:
how far, and what it costs); the record keeps its key, time and
concentration, with its "aim" and "cells" set anew. A record also keeps the
"slot_level" it was cast with, for its damage when it acts.

An area that isn't aimed (an Emanation, a Sphere around the source) follows
its caster, worked out from where the caster is now; any other stays on the
cells it covered when it was put down (a Cone or Line aimed from the caster
doesn't swing round as the caster walks on).

A wall (step 25) keeps its other "end" (none for a ring, aimed at its
middle), "ring", and, for one with a damaging side (Wall of Fire), the
"side" picked and its "side_cells", where a turn ending acts too. A wall
whose rules block movement (Wall of Force), or give cover or make its space
Difficult Terrain (Blade Barrier), keeps that as "terrain", a MapObject's
dict:
`with_kept_walls` lays it over the painted terrain for the rules to read
while the wall lasts, never into the painted map or the log's terrain.
"""

from __future__ import annotations

import math
import uuid
from dataclasses import dataclass
from typing import Iterable

from dataclasses import replace

from Combat.Arena.arena import ArenaSettings, footprint
from Combat.Arena.areas import (
    AreaOfEffect,
    AreaShape,
    area_cells,
    side_cells,
    wall_end,
)
from Combat.Arena.geometry import Cell
from Combat.Arena.terrain import NO_COVER, WALL, MapObject, Terrain
from Combat.Definitions import ActionCost
from Model.Content.ActionType import ActionType
from Model.Content.CombatArea import DEFAULT_TIMING as _DEFAULT_ACTS
from Model.Content.CombatArea import AreaTiming, CombatArea

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
    # A wall's damaging side (Wall of Fire): where a turn ending acts too.
    side: frozenset[Cell] = frozenset()

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
    end: Cell | None = None,
    side: int = 0,
    rules: CombatArea | None = None,
) -> dict:
    """The "area" an active spell keeps for `area` aimed at `aim` by
    `source`: its cells now, unless it follows its caster, with a key of
    its own, what it was picked as and its rules text (`pick`, `about`,
    shown only), and its pick's CombatArea (`rules`: when it acts, how it's
    moved, what it hides). A Wall's other `end` and its damaging `side`
    (areas.side_of) are kept too, with the terrain its rules give it
    (wall_terrain)."""
    follows = not area.is_aimed
    if area.is_wall and aim is not None:
        end = wall_end(area, aim, end, settings)  # where its length stops it
    cells = [] if follows else sorted(area_cells(area, source, aim, settings, end))
    record = {
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
        "rules": rules.to_dict() if rules is not None else None,
    }
    if area.is_wall and aim is not None:
        record["end"] = end.to_list() if end is not None and not area.ring else None
        record["ring"] = area.ring
        reach = rules.side_ft if rules is not None else None
        if side and reach is not None:
            near = side_cells(area, aim, end, side, reach, settings)
            record["side"] = side
            record["side_cells"] = [cell.to_list() for cell in sorted(near)]
        thing = wall_terrain(pick or "Wall", rules)
        if thing is not None:
            record["terrain"] = thing.to_dict()
    return record


def wall_terrain(name: str, rules: CombatArea | None) -> MapObject | None:
    """What a wall is as terrain while it lasts, as its rules say: one that
    blocks movement (Wall of Force) is Total Cover too, as a painted wall
    is; one that gives Three-Quarters Cover and makes its space Difficult
    Terrain (Blade Barrier) is that; None for one that does neither (Wall
    of Fire, Wall of Thorns), or with no rules."""
    if rules is None or not rules.is_wall:
        return None
    if not (rules.blocks or rules.cover or rules.difficult):
        return None
    cover = rules.cover.value if rules.cover is not None else NO_COVER
    return MapObject(name, blocks=rules.blocks, difficult=rules.difficult, cover=cover)


def record_rules(record: dict, name: str = "") -> CombatArea | None:
    """The CombatArea a kept record's pick has ("rules"). A record kept
    before 2026-11-19 has none: those of the spell it was picked as (its
    "pick", or `name`, its active spell's), if there's one by that name."""
    if "rules" in record:
        data = record["rules"]
        return CombatArea.from_dict(data, "a kept area") if data else None
    # Imported here: the map's rules don't otherwise need the spells.
    from CharacterContent.Spells.SpellFactory import SpellFactory

    for wanted in (record.get("pick"), name):
        if wanted:
            try:
                return SpellFactory.create(wanted).combat_area
            except ValueError:
                continue
    return None


def with_kept_walls(settings: ArenaSettings, chars: Iterable[dict]) -> ArenaSettings:
    """The map as the rules read it: `settings` with each kept wall's terrain
    (wall_terrain) on its cells while it lasts, over what's painted there (a
    painted wall stays one; an object that blocks stays, under a wall that
    doesn't). A copy, for reading: `settings` itself when no wall adds
    anything, so the painted map and the log never get it."""
    overlay: dict[Cell, MapObject] = {}
    for char in chars:
        for entry in char.get(ACTIVE_SPELLS_KEY) or []:
            record = entry.get(AREA_KEY) or {}
            data = record.get("terrain")
            if not isinstance(data, dict):
                continue
            thing = MapObject.from_dict(data)
            for cell in record_cells(record, char, settings):
                here = overlay.get(cell)
                if here is None or (thing.blocks and not here.blocks):
                    overlay[cell] = thing
    if not overlay:
        return settings
    cells = dict(settings.terrain.cells)
    for cell, thing in overlay.items():
        spot = settings.terrain.at(cell)
        if spot.ground == WALL:
            continue
        if spot.thing is not None and spot.thing.blocks and not thing.blocks:
            continue
        cells[cell] = replace(spot, thing=thing)
    return replace(settings, terrain=Terrain(cells))


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
        bool(record.get("ring", False)),
    )


def record_end(record: dict) -> Cell | None:
    """A straight wall's other end, if its record has one."""
    end = record.get("end")
    return Cell.of(end) if end is not None else None


def record_origin(record: dict) -> list[Cell] | None:
    """Where an aimed area spreads from, for the cover against it: the cell
    a point area was aimed at (a Fireball's), or None for one that starts
    at its source (a Cone, an Emanation), whose cover is the source's. A
    wall has no point of origin: it's where it is, so its own cells, with
    nothing between it and who's in it."""
    area = record_area(record)
    if area.is_wall:
        return [Cell.of(c) for c in record.get("cells", [])] or None
    if area.starts_at_source or record.get("aim") is None:
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
            side = (Cell.of(c) for c in record.get("side_cells") or [])
            found.append(
                LastingArea(
                    caster=char["name"],
                    name=entry["name"],
                    cells=frozenset(cells),
                    color=record.get("color") or DEFAULT_AREA_COLOR,
                    concentration=bool(entry.get("concentration")),
                    key=area_key(char, entry),
                    side=frozenset(c for c in side if settings.on_map(c)),
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


def areas_beside(
    char: dict, areas: Iterable[LastingArea], settings: ArenaSettings
) -> list[LastingArea]:
    """The walls char is by the damaging side of (Wall of Fire's "within 10
    feet of that side") and not in."""
    own = set(footprint(char, settings.distance_rule))
    return [
        area
        for area in areas
        if own.intersection(area.side) and not own.intersection(area.cells)
    ]


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


# When a kept area acts on a creature (record_timing): as it enters the
# area, as the area moves onto it (moved, or an Emanation following its
# caster), and as its turn starts or ends there (CombatArea.acts).
ENTERS = AreaTiming.ENTERS.value
MOVED_ONTO = AreaTiming.MOVED_ONTO.value
STARTS = AreaTiming.STARTS.value
ENDS = AreaTiming.ENDS.value
# What an area whose rules say none of these does: what the reminders said
# before step 24, a creature entering it or starting its turn in it.
DEFAULT_TIMING = frozenset(when.value for when in _DEFAULT_ACTS)
_ACTION_NAMES = {
    ActionType.ACTION: ActionCost.ACTION,
    ActionType.BONUS_ACTION: ActionCost.BONUS_ACTION,
}


def area_timing(rules: CombatArea | None) -> frozenset[str]:
    """When an area with `rules` acts on a creature: ENTERS, MOVED_ONTO,
    STARTS and ENDS as its `acts` say (Moonbeam's ENTERS, MOVED_ONTO and
    ENDS), DEFAULT_TIMING for rules that say none, or none."""
    return rules.timing if rules is not None else DEFAULT_TIMING


def record_timing(record: dict, name: str = "") -> frozenset[str]:
    """When a kept area acts on a creature, as its rules say (record_rules)."""
    return area_timing(record_rules(record, name))


@dataclass(frozen=True)
class MoveRule:
    """How a kept area is moved: up to `feet` (None: its rules don't say),
    costing its caster `action` (ActionCost.ACTION or ActionCost.BONUS_ACTION; None: nothing, or
    its rules don't say)."""

    feet: int | None = None
    action: str | None = None

    @property
    def text(self) -> str:
        """ "up to 60 ft., an Action"; "" when its rules say neither."""
        parts = []
        if self.feet is not None:
            parts.append(f"up to {self.feet} ft.")
        if self.action is not None:
            parts.append(
                f"a{'n' if self.action == ActionCost.ACTION else ''} {self.action}"
            )
        return ", ".join(parts)


def move_rule(rules: CombatArea | None) -> MoveRule:
    """How far and at what cost an area with `rules` moves: its `move_ft`
    and `move_action` (Flaming Sphere's 30 feet for a Bonus Action,
    Moonbeam's 60 for an Action)."""
    if rules is None:
        return MoveRule()
    action = _ACTION_NAMES.get(rules.move_action) if rules.move_action else None
    return MoveRule(rules.move_ft, action)


def record_move(record: dict, name: str = "") -> MoveRule:
    """How a kept area moves, as its rules say (record_rules)."""
    return move_rule(record_rules(record, name))


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
    # A turn that ended by a wall's damaging side, not in the wall (step 25).
    beside: bool = False

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
        (entered it)", "... (ended its turn by its damaging side)"."""
        when = _WHEN_TEXT[self.when]
        if self.beside:
            when = "ended its turn by its damaging side"
        return f"{self.title} on {self.target['name']} ({when})"
