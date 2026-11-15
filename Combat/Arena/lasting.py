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
    }

An area that isn't aimed (an Emanation, a Sphere around the source) follows
its caster, worked out from where the caster is now; any other stays on the
cells it covered when it was put down (a Cone or Line aimed from the caster
doesn't swing round as the caster walks on).
"""

from __future__ import annotations

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
) -> dict:
    """The "area" an active spell keeps for `area` aimed at `aim` by
    `source`: its cells now, unless it follows its caster."""
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
    }


def record_area(record: dict) -> AreaOfEffect:
    """The AreaOfEffect a kept record describes."""
    return AreaOfEffect(
        AreaShape(record["shape"]),
        int(record["size_ft"]),
        int(record.get("width_ft", 5)),
        bool(record.get("from_source", False)),
    )


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
