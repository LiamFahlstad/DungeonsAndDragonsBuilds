"""Areas of effect on the battle map, with no Qt (Notes/combat-arena-plan.md,
step 10): which cells a Sphere, Cylinder, Cube, Cone, Line or Emanation
covers, aimed at a cell, and which creatures stand in them.

The shapes are the Rules Glossary's (Areas of Effect). On the grid:

- A cell is in an area when its middle is (the area covers most of it).
- A Sphere or a Cylinder is centred on the cell aimed at, and its radius is
  counted by the map's distance rule, as every distance on the map is: a
  creature the hover calls "20 ft." away is inside a 20-foot-radius Sphere.
  Its point of origin is in it, so it can catch its creator.
- An Emanation reaches its distance from the source's nearest cell, by the
  same rule, and leaves the source out ("isn't included unless its creator
  decides otherwise"). A Sphere or Cylinder "centered on you" is one too.
- A Cone and a Line go from the source towards the cell aimed at, in any
  direction, and reach no further than their length by the same rule, from
  the source's nearest cell: nothing in a 15-foot Cone is more than "15
  ft." away on the hover. Their direction is taken from the middle of the
  source's space. A Line covers the cells its path crosses, as many wide as
  it says (5 ft. unless said): one unbroken row of cells, each a step
  further than the last, at any angle. A Cone is as wide at each point as
  it is far from the middle of the source (the glossary's "width ... equal
  to that point's distance from the point of origin"), and covers its own
  5-foot spine too, so it's never empty or broken aimed diagonally.
- A Cube is centred on the cell aimed at, or, from the source (Thunderwave),
  set against the side of the source's space nearest the cell aimed at.

Cells are reached through geometry's GridShape and DistanceRule only (the
plan's Decision 3): directions are worked out from the shape's cell
centres, never from a cell's coordinates.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from Combat.Arena.arena import ArenaSettings, footprint
from Combat.Arena.cover import reaches
from Combat.Arena.geometry import Cell

_EPSILON = 1e-9


class AreaShape(str, Enum):
    SPHERE = "Sphere"
    CYLINDER = "Cylinder"
    CUBE = "Cube"
    CONE = "Cone"
    LINE = "Line"
    EMANATION = "Emanation"


# Shapes whose size is a radius ("20-foot-radius Sphere").
_BY_RADIUS = (AreaShape.SPHERE, AreaShape.CYLINDER)
# Shapes that always start at the source.
_FROM_SOURCE = (AreaShape.CONE, AreaShape.LINE, AreaShape.EMANATION)


@dataclass(frozen=True)
class AreaOfEffect:
    """An area: its shape and size in feet (a Sphere's or Cylinder's radius,
    a Cone's or Line's length, a Cube's side, an Emanation's distance), a
    Line's width, and whether a Sphere, Cylinder or Cube starts at the
    source rather than at a point (Cones, Lines and Emanations always do)."""

    shape: AreaShape
    size_ft: int
    width_ft: int = 5
    from_source: bool = False

    @property
    def starts_at_source(self) -> bool:
        return self.shape in _FROM_SOURCE or self.from_source

    @property
    def is_aimed(self) -> bool:
        """Whether where it goes depends on the cell aimed at: not for an
        Emanation, or a Sphere or Cylinder around the source."""
        if self.shape is AreaShape.EMANATION:
            return False
        return not (self.shape in _BY_RADIUS and self.from_source)

    @property
    def text(self) -> str:
        """ "20-foot-radius Sphere", "15-foot Cone", "100-foot-long,
        5-foot-wide Line", "15-foot Cube from you"."""
        shape = self.shape.value
        if self.shape in _BY_RADIUS:
            text = f"{self.size_ft}-foot-radius {shape}"
        elif self.shape is AreaShape.LINE:
            text = f"{self.size_ft}-foot-long, {self.width_ft}-foot-wide {shape}"
        else:
            text = f"{self.size_ft}-foot {shape}"
        if self.from_source and self.shape not in _FROM_SOURCE:
            text += " around you" if self.shape in _BY_RADIUS else " from you"
        return text


_SHAPES = "|".join(s.value for s in AreaShape)
_NUMBER = r"(\d[\d,]*)"
_FOOT = r"[- ](?:foot|feet|ft\.?)"
# "20-foot-radius Sphere", "10-foot-radius, 40-foot-high Cylinder",
# "Self (10-foot-radius sphere)", "20-foot radius sphere".
_RADIUS = re.compile(
    rf"{_NUMBER}{_FOOT}[- ]radius,?(?:\s+{_NUMBER}{_FOOT}[- ]high,?)?\s+"
    r"(sphere|cylinder|emanation)?",
    re.IGNORECASE,
)
# "100-foot-long, 5-foot-wide Line", "Line 100 feet long and 5 feet wide".
_LONG_LINE = re.compile(
    rf"{_NUMBER}{_FOOT}[- ]long,?\s+{_NUMBER}{_FOOT}[- ]wide\s+line",
    re.IGNORECASE,
)
# "5-foot-wide, 60-foot-long Line" (Sunbeam).
_WIDE_LINE = re.compile(
    rf"{_NUMBER}{_FOOT}[- ]wide,?\s+{_NUMBER}{_FOOT}[- ]long\s+line",
    re.IGNORECASE,
)
# A 2014 range of "Self (10-foot radius)": a Sphere around the source.
_SELF_RADIUS = re.compile(
    rf"self\s*\(\s*{_NUMBER}{_FOOT}[- ]radius(?:\s+sphere)?\s*\)", re.IGNORECASE
)
# How far away the point an area is centred on may be: "a point you can see
# within 60 feet of you", "centered on a point within 120 feet".
_POINT_WITHIN = re.compile(
    rf"\bpoint\b[^.]{{0,30}}?within {_NUMBER}{_FOOT}", re.IGNORECASE
)
# A spell's range: "150 feet", "1,000 feet", "1 mile", "Touch".
_RANGE_FEET = re.compile(rf"^\s*{_NUMBER}\s+(?:foot|feet)\b", re.IGNORECASE)
_RANGE_MILES = re.compile(rf"^\s*{_NUMBER}\s+miles?\b", re.IGNORECASE)
FEET_PER_MILE = 5280
TOUCH_FT = 5
_LINE_LONG = re.compile(
    rf"\bline\b(?:\s+of\s+[a-z ]{{1,30}}?)?\s+{_NUMBER}\s+(?:foot|feet)\s+long"
    rf"(?:\s+and\s+{_NUMBER}\s+"
    r"(?:foot|feet)\s+wide)?",
    re.IGNORECASE,
)
# "15-foot Cone", "30-foot Emanation", "15-foot cube", "60-foot line", and
# "20-foot square" (Entangle, Grease): a Cube on the ground.
_SIZED = re.compile(rf"{_NUMBER}{_FOOT}\s+({_SHAPES}|square)\b", re.IGNORECASE)
# "Each creature within 5 feet of that point" (Call Lightning): a Sphere.
_WITHIN_POINT = re.compile(
    rf"(?:each|every|all)(?: other)? creatures?[^.]{{0,40}}?within {_NUMBER}"
    rf"{_FOOT} of (?:that|the|a) point\b",
    re.IGNORECASE,
)
# "each creature within 5 feet of you", "All other creatures within 5 feet of
# you" (Sword Burst), "within 10 feet of it": an Emanation.
_WITHIN = re.compile(
    rf"(?:each|every|all)(?: other)? creatures?[^.]{{0,40}}?within {_NUMBER}"
    rf"{_FOOT} of (?!(?:that|the|a) point\b)"
    r"(?:you|it|itself|the \w+|him|her|them)\b",
    re.IGNORECASE,
)
# What says the area is the source's own: "Self (15-foot cube)", "centered on
# you", "originating from you".
_AROUND_SOURCE = re.compile(
    r"\bself\s*\(|centered on (?:you|yourself|itself|himself|herself)\b"
    r"|originat\w* from (?:you|yourself|itself)\b",
    re.IGNORECASE,
)


def _feet(text: str | None) -> int:
    return int((text or "0").replace(",", ""))


def parse_area(text: str) -> AreaOfEffect | None:
    """The first area of effect `text` states ("Each creature in a
    20-foot-radius Sphere centered on that point"), or None when it states
    none."""
    found: list[tuple[int, AreaOfEffect]] = []
    for match in _RADIUS.finditer(text):
        shape_name = (match.group(3) or "sphere").title()
        shape = AreaShape(shape_name)
        size = _feet(match.group(1))
        if size:
            found.append((match.start(), AreaOfEffect(shape, size)))
    for match in _LONG_LINE.finditer(text):
        found.append(
            (
                match.start(),
                AreaOfEffect(
                    AreaShape.LINE, _feet(match.group(1)), _feet(match.group(2))
                ),
            )
        )
    for match in _WIDE_LINE.finditer(text):
        found.append(
            (
                match.start(),
                AreaOfEffect(
                    AreaShape.LINE, _feet(match.group(2)), _feet(match.group(1))
                ),
            )
        )
    for match in _SELF_RADIUS.finditer(text):
        found.append(
            (
                match.start(),
                AreaOfEffect(AreaShape.SPHERE, _feet(match.group(1)), from_source=True),
            )
        )
    for match in _LINE_LONG.finditer(text):
        width = _feet(match.group(2)) or 5
        found.append(
            (match.start(), AreaOfEffect(AreaShape.LINE, _feet(match.group(1)), width))
        )
    for match in _SIZED.finditer(text):
        size = _feet(match.group(1))
        if size:
            name = match.group(2).title()
            shape = AreaShape.CUBE if name == "Square" else AreaShape(name)
            found.append((match.start(), AreaOfEffect(shape, size)))
    for match in _WITHIN_POINT.finditer(text):
        size = _feet(match.group(1))
        if size:
            found.append((match.start(), AreaOfEffect(AreaShape.SPHERE, size)))
    for match in _WITHIN.finditer(text):
        size = _feet(match.group(1))
        if size:
            found.append((match.start(), AreaOfEffect(AreaShape.EMANATION, size)))
    if not found:
        return None
    start, area = min(found, key=lambda item: item[0])
    if area.shape in (AreaShape.SPHERE, AreaShape.CYLINDER, AreaShape.CUBE):
        # "Self (15-foot cube)", or the area's own sentence says so.
        end = text.find(".", start)
        sentence = text[text.rfind(".", 0, start) + 1 : end if end >= 0 else None]
        before = text[max(0, start - 8) : start]
        if _AROUND_SOURCE.search(sentence) or _AROUND_SOURCE.search(before):
            area = AreaOfEffect(area.shape, area.size_ft, area.width_ft, True)
    return area


def _centre(cells: Iterable[Cell], settings: ArenaSettings) -> tuple[float, float]:
    """The middle of `cells`, in cells (each a unit across)."""
    shape = settings.distance_rule.shape
    points = [shape.center(cell, 1.0) for cell in cells]
    return (
        sum(x for x, _ in points) / len(points),
        sum(y for _, y in points) / len(points),
    )


def _within(
    settings: ArenaSettings, origins: list[Cell], feet: int, leave_out: set[Cell]
) -> set[Cell]:
    """Every map cell within `feet` of the nearest of `origins`, by the
    map's distance rule, but those in `leave_out`."""
    rule, shape = settings.distance_rule, settings.distance_rule.shape
    return {
        cell
        for cell in shape.cells(settings.width, settings.height)
        if cell not in leave_out
        and min(rule.feet(o, cell, settings.cell_ft) for o in origins) <= feet
    }


def _along(
    settings: ArenaSettings,
    source: list[Cell],
    aim: Cell,
    length_ft: int,
    width_cells: int,
    widens: bool,
) -> set[Cell]:
    """The cells of a Line (`widens` False) or a Cone (True) from `source`
    towards `aim`: each cell ahead of the middle of the source, within
    `length_ft` of the source's nearest cell by the map's rule, and on the
    path `width_cells` cells wide; a Cone also takes each cell no further
    to the side than half as far as it is ahead.

    A cell is on the path when the path's band crosses its square: a
    square reaches half(|ux| + |uy|) to either side of its middle, seen
    across the direction (ux, uy). The band is open on one side, so a path
    one cell wide is a single unbroken row, also exactly on a diagonal; a
    Cone's spine is closed on both, so it stays even on both sides."""
    rule = settings.distance_rule
    shape = rule.shape
    ox, oy = _centre(source, settings)
    ax, ay = shape.center(aim, 1.0)
    dx, dy = ax - ox, ay - oy
    norm = math.hypot(dx, dy)
    if norm < _EPSILON:
        return set()
    ux, uy = dx / norm, dy / norm
    reach = 0.5 * (abs(ux) + abs(uy))  # a square's half-width across the path
    band = width_cells * reach
    own = set(source)
    cells = set()
    for cell in shape.cells(settings.width, settings.height):
        if cell in own:
            continue
        if min(rule.feet(o, cell, settings.cell_ft) for o in own) > length_ft:
            continue
        x, y = shape.center(cell, 1.0)
        vx, vy = x - ox, y - oy
        ahead = vx * ux + vy * uy
        if ahead <= _EPSILON:
            continue
        side = vx * uy - vy * ux  # signed: which side of the path
        if widens:
            if abs(side) <= max(ahead / 2, reach) + _EPSILON:
                cells.add(cell)
        elif -band + _EPSILON < side <= band + _EPSILON:
            cells.add(cell)
    return cells


def _cube_at(settings: ArenaSettings, aim: Cell, across: int) -> set[Cell]:
    shape = settings.distance_rule.shape
    back = -((across - 1) // 2)
    anchor = shape.offset(aim, back, back)
    return {c for c in shape.footprint(anchor, across) if settings.on_map(c)}


def _cube_beside(
    settings: ArenaSettings, source: list[Cell], aim: Cell, across: int
) -> set[Cell]:
    """A Cube `across` cells on a side against one side of `source`'s space,
    the one whose middle is nearest `aim`."""
    shape = settings.distance_rule.shape
    own = set(source)
    touching = {n for cell in source for n in shape.neighbours(cell)} - own
    corner = source[0]
    space = round(math.sqrt(len(source)))
    ax, ay = shape.center(aim, 1.0)
    best: tuple[float, Cell] | None = None
    for cols in range(-across, space + 1):
        for rows in range(-across, space + 1):
            anchor = shape.offset(corner, cols, rows)
            cells = shape.footprint(anchor, across)
            if own.intersection(cells) or not touching.intersection(cells):
                continue
            cx, cy = _centre(cells, settings)
            key = (math.hypot(cx - ax, cy - ay), anchor)
            if best is None or key < best:
                best = key
    if best is None:
        return set()
    return {c for c in shape.footprint(best[1], across) if settings.on_map(c)}


def point_of_origin(
    area: AreaOfEffect, source: dict | None, aim: Cell | None, settings: ArenaSettings
) -> list[Cell]:
    """Where `area` spreads from (Rules Glossary, Area of Effect): the cell
    aimed at for one centred on a point, else the source's cells (a Cone,
    a Line, an Emanation, Thunderwave's Cube); none without them."""
    if area.starts_at_source:
        return footprint(source, settings.distance_rule) if source is not None else []
    return [aim] if aim is not None else []


def area_cells(
    area: AreaOfEffect,
    source: dict | None,
    aim: Cell | None,
    settings: ArenaSettings,
) -> set[Cell]:
    """The map cells `area` covers, aimed at `aim` (None: not aimed yet) by
    `source`; none when it needs a source or an aim it doesn't have. A cell
    behind Total Cover from its point of origin isn't in it (a wall, a
    closed door: Combat/Arena/cover.py)."""
    cells = _shape_cells(area, source, aim, settings)
    if not cells or not settings.terrain:
        return cells
    origins = point_of_origin(area, source, aim, settings)
    return {cell for cell in cells if reaches(origins, cell, settings)}


def _shape_cells(
    area: AreaOfEffect,
    source: dict | None,
    aim: Cell | None,
    settings: ArenaSettings,
) -> set[Cell]:
    """The cells of area's shape, nothing in the way counted."""
    rule = settings.distance_rule
    own = footprint(source, rule) if source is not None else []
    if area.starts_at_source and not own:
        return set()
    if area.is_aimed and aim is None:
        return set()
    cell_ft = settings.cell_ft
    if not area.is_aimed:
        return _within(settings, own, area.size_ft, set(own))
    assert aim is not None
    if area.shape in _BY_RADIUS:
        return _within(settings, [aim], area.size_ft, set())
    across = max(1, area.size_ft // cell_ft)
    if area.shape is AreaShape.CUBE:
        if area.from_source:
            return _cube_beside(settings, own, aim, across)
        return _cube_at(settings, aim, across)
    if area.shape is AreaShape.CONE:
        return _along(settings, own, aim, area.size_ft, 1, widens=True)
    width = max(1, round(area.width_ft / cell_ft))
    return _along(settings, own, aim, area.size_ft, width, widens=False)


def creatures_in(
    chars: Iterable[dict], cells: set[Cell], settings: ArenaSettings
) -> list[dict]:
    """Who is in `cells`, in `chars`' order: anyone with a cell of their
    space in them (a creature is in an area that touches any of it)."""
    rule = settings.distance_rule
    return [c for c in chars if cells.intersection(footprint(c, rule))]


def spell_range_ft(range_text: str) -> int | None:
    """How far a spell reaches, from its range ("150 feet", "1 mile",
    "Touch"); None for Self, Sight, Unlimited and Special, which a point
    can't be checked against."""
    match = _RANGE_FEET.match(range_text)
    if match:
        return _feet(match.group(1))
    match = _RANGE_MILES.match(range_text)
    if match:
        return _feet(match.group(1)) * FEET_PER_MILE
    if range_text.strip().lower() == "touch":
        return TOUCH_FT
    return None


def point_range_ft(text: str) -> int | None:
    """How far away a rules text lets the point an area is centred on be
    ("a 20-foot-radius Sphere centered on a point within 120 feet"), or
    None when it doesn't say."""
    match = _POINT_WITHIN.search(text)
    return _feet(match.group(1)) if match else None
