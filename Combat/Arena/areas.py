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

A wall (Wall of Fire, Wall of Force, Blade Barrier, Wall of Thorns; step 25)
isn't one of the glossary's six shapes and has no point of origin, so
nothing it crosses cuts it. On the grid it's a Wall: a straight one is the
cells a line between its two ends' middles crosses (both ends in it, a
corner's two cells both), as far from its first end as its length lets by
the map's rule; a ring (`ring`) is the edge of a Sphere half its size
across, around the cell aimed at: each cell within that distance with a
neighbour beyond it, so nothing walks through either. However thick its
text says, it's one cell thick (1 to 5 feet in every wall here). A wall
with a damaging side (Wall of Fire's "One side of the wall") keeps the
cells within the distance its text says of that side (`side_cells`).

Cells are reached through geometry's GridShape and DistanceRule only (the
plan's Decision 3): directions are worked out from the shape's cell
centres, never from a cell's coordinates.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable

from Combat.Arena.arena import ArenaSettings, footprint
from Combat.Arena.cover import reaches
from Combat.Arena.geometry import Cell
from Model.Content.CombatArea import CombatArea
from Model.Content.CombatArea import CombatAreaShape as AreaShape

_EPSILON = 1e-9


# Shapes whose size is a radius ("20-foot-radius Sphere").
_BY_RADIUS = (AreaShape.SPHERE, AreaShape.CYLINDER)
# Shapes that always start at the source.
_FROM_SOURCE = (AreaShape.CONE, AreaShape.LINE, AreaShape.EMANATION)


@dataclass(frozen=True)
class AreaOfEffect:
    """An area as the map aims it: its shape and size in feet (a Sphere's or
    Cylinder's radius, a Cone's or Line's length, a Cube's side, an
    Emanation's distance, a Wall's length or a ring's distance across), a
    Line's width (a Wall's thickness), whether a Sphere, Cylinder or Cube
    starts at the source rather than at a point (Cones, Lines and
    Emanations always do), and whether a Wall is a ring. The shape is the
    model's CombatAreaShape (Model/Content/CombatArea.py); a spell's or a
    feature's CombatArea gives one with area_of."""

    shape: AreaShape
    size_ft: int
    width_ft: int = 5
    from_source: bool = False
    ring: bool = False

    @property
    def is_wall(self) -> bool:
        return self.shape is AreaShape.WALL

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
        5-foot-wide Line", "15-foot Cube from you", "60-foot-long Wall",
        "Wall in a 20-foot ring"."""
        shape = self.shape.value
        if self.shape is AreaShape.WALL:
            if self.ring:
                return f"Wall in a {self.size_ft}-foot ring"
            return f"{self.size_ft}-foot-long Wall"
        if self.shape in _BY_RADIUS:
            text = f"{self.size_ft}-foot-radius {shape}"
        elif self.shape is AreaShape.LINE:
            text = f"{self.size_ft}-foot-long, {self.width_ft}-foot-wide {shape}"
        else:
            text = f"{self.size_ft}-foot {shape}"
        if self.from_source and self.shape not in _FROM_SOURCE:
            text += " around you" if self.shape in _BY_RADIUS else " from you"
        return text


def area_of(rules: CombatArea | None) -> AreaOfEffect | None:
    """The area a spell's or a feature's CombatArea aims on the map (its
    shape, size, width and whether it starts at the source); None for
    none."""
    if rules is None:
        return None
    return AreaOfEffect(rules.shape, rules.size_ft, rules.width_ft, rules.from_source)


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


def wall_cells(
    area: AreaOfEffect, aim: Cell, end: Cell | None, settings: ArenaSettings
) -> set[Cell]:
    """The map cells a Wall covers: a ring around `aim`, or a straight wall
    from `aim` to `end` (just `aim` while the other end isn't clicked yet),
    no further from `aim` than its length lets by the map's rule (a
    60-foot wall along a row is 12 cells)."""
    rule, shape = settings.distance_rule, settings.distance_rule.shape
    cell_ft = settings.cell_ft
    if area.ring:
        radius = max(cell_ft, area.size_ft // 2)
        return {
            cell
            for cell in shape.cells(settings.width, settings.height)
            if rule.feet(aim, cell, cell_ft) <= radius
            and any(rule.feet(aim, n, cell_ft) > radius for n in rule.neighbours(cell))
        }
    return {cell for step in _wall_steps(area, aim, end, settings) for cell in step}


def _wall_steps(
    area: AreaOfEffect, aim: Cell, end: Cell | None, settings: ArenaSettings
) -> list[tuple[Cell, ...]]:
    """A straight wall's cells from `aim` towards `end`, in order, a
    corner's two cells as one step, as far as its length lets."""
    rule, shape = settings.distance_rule, settings.distance_rule.shape
    cell_ft = settings.cell_ft
    steps: list[tuple[Cell, ...]] = [(aim,)]
    if end is not None and end != aim:
        steps += shape.crossed(aim, end) + [(end,)]
    longest = max(0, area.size_ft - cell_ft)
    kept = []
    for step in steps:
        cells = tuple(
            c
            for c in step
            if settings.on_map(c) and rule.feet(aim, c, cell_ft) <= longest
        )
        if cells:
            kept.append(cells)
    return kept


def wall_end(
    area: AreaOfEffect, aim: Cell, end: Cell | None, settings: ArenaSettings
) -> Cell | None:
    """Where a straight wall from `aim` towards `end` really ends: `end`, or
    the last cell its length reaches on the way (a 60-foot wall clicked 75
    ft. long stops short); None for a ring or with no `end`."""
    if area.ring or end is None:
        return None
    singles = [s[0] for s in _wall_steps(area, aim, end, settings) if len(s) == 1]
    return singles[-1] if singles else None


def side_of(
    area: AreaOfEffect, aim: Cell, end: Cell | None, cell: Cell, settings: ArenaSettings
) -> int:
    """Which side of a Wall `cell` is on: for a ring, 1 inside and -1
    outside; for a straight wall from `aim` to `end`, 1 or -1 by which side
    of the line through their middles its middle is. 0 on the wall's line
    (or a ring's edge), or for a straight wall with one end."""
    rule, shape = settings.distance_rule, settings.distance_rule.shape
    if area.ring:
        radius = max(settings.cell_ft, area.size_ft // 2)
        feet = rule.feet(aim, cell, settings.cell_ft)
        return 1 if feet < radius else (-1 if feet > radius else 0)
    if end is None or end == aim:
        return 0
    ax, ay = shape.center(aim, 1.0)
    bx, by = shape.center(end, 1.0)
    cx, cy = shape.center(cell, 1.0)
    cross = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
    if abs(cross) < _EPSILON:
        return 0
    return 1 if cross > 0 else -1


def side_cells(
    area: AreaOfEffect,
    aim: Cell,
    end: Cell | None,
    side: int,
    reach_ft: int,
    settings: ArenaSettings,
) -> set[Cell]:
    """The cells within `reach_ft` of a Wall, by the map's rule from its
    nearest cell, on its `side` (side_of): Wall of Fire's damaging side."""
    wall = wall_cells(area, aim, end, settings)
    if not wall or side == 0:
        return set()
    rule, cell_ft = settings.distance_rule, settings.cell_ft
    return {
        cell
        for cell in rule.shape.cells(settings.width, settings.height)
        if cell not in wall
        and side_of(area, aim, end, cell, settings) == side
        and min(rule.feet(w, cell, cell_ft) for w in wall) <= reach_ft
    }


def side_name(area: AreaOfEffect, aim: Cell, end: Cell | None, side: int) -> str:
    """ "inside" or "outside" a ring; for a straight wall, the way its side
    faces ("north", "south-west"), by the side's direction on the map (up is
    north)."""
    if area.ring:
        return "inside" if side > 0 else "outside"
    if end is None or side == 0:
        return ""
    dx, dy = end.col - aim.col, end.row - aim.row
    # The side's normal: to the right of the wall's direction for side 1
    # (y grows downward, so a positive cross is clockwise of it).
    nx, ny = (-dy, dx) if side > 0 else (dy, -dx)
    angle = math.degrees(math.atan2(-ny, nx)) % 360
    names = ("east", "north-east", "north", "north-west", "west", "south-west")
    names += ("south", "south-east")
    return names[int((angle + 22.5) // 45) % 8]


def area_cells(
    area: AreaOfEffect,
    source: dict | None,
    aim: Cell | None,
    settings: ArenaSettings,
    end: Cell | None = None,
) -> set[Cell]:
    """The map cells `area` covers, aimed at `aim` (None: not aimed yet) by
    `source`; none when it needs a source or an aim it doesn't have. A cell
    behind Total Cover from its point of origin isn't in it (a wall, a
    closed door: Combat/Arena/cover.py). A Wall goes from `aim` to `end`
    (wall_cells), and has no point of origin to be cut off from."""
    if area.is_wall:
        return wall_cells(area, aim, end, settings) if aim is not None else set()
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
