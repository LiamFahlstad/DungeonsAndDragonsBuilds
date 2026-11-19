"""Cover from the battle map, with no Qt (Notes/combat-arena-plan.md, step
19; the map-painter plan's Q2).

The Rules Glossary (Cover): "Half Cover (+2 bonus to AC and Dexterity saving
throws), Three-Quarters Cover (+5 bonus to AC and Dexterity saving throws),
and Total Cover (can't be targeted directly). If behind more than one degree
of cover, a target benefits only from the most protective degree." The
Player's Handbook names what gives Half Cover: "a low wall, a large piece of
furniture, a narrow tree trunk, or a creature, whether that creature is an
enemy or a friend".

On the grid (Decision 30):

- Cover is counted along the straight line between the middles of a cell of
  the attacker's (or of an area's point of origin) and a cell of the
  target's, over every such pair, and the line with the least cover is the
  one that counts: the attacker picks its best line, as at a table.
- What the line crosses gives cover, its two ends left out: a wall Total
  Cover, a painted object its own, and another creature Half Cover (one at
  0 HP lies on the ground and gives none). A line passing exactly through
  a corner squeezes between two cells and is covered only as much as the
  less protective of them.
- Height isn't counted: a creature on a ledge is behind a low wall as one
  on the ground is.
- An area of effect stops at Total Cover (Rules Glossary, Area of Effect: a
  location no unblocked straight line from the point of origin reaches
  isn't in it); there only the terrain counts, as a creature never gives
  Total Cover.

Cells are reached through geometry's GridShape only (the plan's Decision 3).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from Combat.Arena.arena import ArenaSettings, footprint
from Combat.Arena.geometry import Cell
from Combat.Arena.terrain import HALF, NO_COVER, THREE_QUARTERS, TOTAL, WALL
from Model.Creatures.Combatants import Visibility

# The terrain's cover keys from the least protective, and the cover each is
# as a target's visibility state (Combat/Effects/modifiers.py's COVER_RULES).
_ORDER = (NO_COVER, HALF, THREE_QUARTERS, TOTAL)
STATES = {
    HALF: Visibility.HALF_COVER.value,
    THREE_QUARTERS: Visibility.THREE_QUARTERS_COVER.value,
    TOTAL: Visibility.TOTAL_COVER.value,
}
# What each gives, for the target label.
BENEFITS = {
    HALF: "+2 AC and DEX saves",
    THREE_QUARTERS: "+5 AC and DEX saves",
    TOTAL: "can't be targeted directly",
}


@dataclass(frozen=True)
class CoverReading:
    """How much cover a line gives (a terrain cover key: terrain.HALF), and
    what gives it ("Barrel at C4", "Goblin", "Wall at D5"); NO_COVER and ""
    for none."""

    degree: str = NO_COVER
    by: str = ""

    def __bool__(self) -> bool:
        return self.degree != NO_COVER

    @property
    def total(self) -> bool:
        return self.degree == TOTAL

    @property
    def state(self) -> str | None:
        """The target's visibility state it is ("Half Cover"), or None."""
        return STATES.get(self.degree)

    @property
    def text(self) -> str:
        """ "Half Cover from Barrel at C4: +2 AC and DEX saves"; "" for none."""
        if not self:
            return ""
        return f"{self.state} from {self.by}: {BENEFITS[self.degree]}"


NO_COVER_READING = CoverReading()


def _more(a: CoverReading, b: CoverReading) -> CoverReading:
    return b if _ORDER.index(b.degree) > _ORDER.index(a.degree) else a


def _less(a: CoverReading, b: CoverReading) -> CoverReading:
    return b if _ORDER.index(b.degree) < _ORDER.index(a.degree) else a


def _in_the_way(char: dict) -> bool:
    """Whether char stands up as an obstacle: not down at 0 HP."""
    hp = char.get("hp")
    return not (isinstance(hp, (int, float)) and hp <= 0)


def _cell_cover(
    cell: Cell,
    settings: ArenaSettings,
    standing: dict[Cell, dict],
) -> CoverReading:
    """What one cell on the line gives: a wall Total Cover, its object its
    own, a creature standing on it Half Cover; the most of these."""
    shape = settings.distance_rule.shape
    where = shape.cell_name(cell)
    spot = settings.terrain.at(cell)
    if spot.ground == WALL:
        return CoverReading(TOTAL, f"Wall at {where}")
    found = NO_COVER_READING
    if spot.thing is not None and spot.thing.cover != NO_COVER:
        found = CoverReading(spot.thing.cover, f"{spot.thing.name} at {where}")
    creature = standing.get(cell)
    if creature is not None:
        found = _more(found, CoverReading(HALF, creature["name"]))
    return found


def line_cover(
    a: Cell,
    b: Cell,
    settings: ArenaSettings,
    standing: dict[Cell, dict],
    leave_out: set[Cell] = frozenset(),  # type: ignore[assignment]
) -> CoverReading:
    """The cover the straight line from a to b crosses: the most protective
    step's, a corner's two cells counting as the less protective one.
    `standing`: who stands on each cell (creatures give Half Cover);
    `leave_out`: cells that give none (the two creatures' own)."""
    found = NO_COVER_READING
    for step in settings.distance_rule.shape.crossed(a, b):
        cells = [c for c in step if c not in leave_out]
        if len(cells) < len(step):
            continue  # beside one of the two creatures' own cells: open
        here = _cell_cover(cells[0], settings, standing)
        for other in cells[1:]:
            here = _less(here, _cell_cover(other, settings, standing))
        found = _more(found, here)
        if found.total:
            return found
    return found


def cover_between(
    origins: Iterable[Cell],
    target: dict,
    chars: Iterable[dict],
    settings: ArenaSettings,
    leave_out: Iterable[dict] = (),
) -> CoverReading:
    """The cover `target` has against something coming from `origins` (an
    attacker's cells, or an area's point of origin): the least over every
    line from one of them to one of target's cells. Nobody gives cover but
    the creatures in `chars` standing in the way, target and `leave_out`
    (the attacker) not among them. None of it when either isn't on the map."""
    rule = settings.distance_rule
    starts = list(origins)
    ends = footprint(target, rule)
    if not starts or not ends:
        return NO_COVER_READING
    skipped = [target, *leave_out]
    standing = {
        cell: char
        for char in chars
        if not any(char is s for s in skipped) and _in_the_way(char)
        for cell in footprint(char, rule)
    }
    own = set(starts) | set(ends)
    best: CoverReading | None = None
    for start in starts:
        for end in ends:
            here = line_cover(start, end, settings, standing, own)
            best = here if best is None else _less(best, here)
            if not best:
                return best
    return best or NO_COVER_READING


def cover_from(
    attacker: dict, target: dict, chars: Iterable[dict], settings: ArenaSettings
) -> CoverReading:
    """The cover target has against attacker (cover_between from attacker's
    cells); none when either is off the map, or they're the same."""
    if attacker is target:
        return NO_COVER_READING
    cells = footprint(attacker, settings.distance_rule)
    return cover_between(cells, target, chars, settings, (attacker,))


def reaches(origins: list[Cell], cell: Cell, settings: ArenaSettings) -> bool:
    """Whether an unblocked straight line from one of `origins` reaches
    `cell`: no wall or Total Cover object crossed on the way (creatures
    don't block an area)."""
    if cell in origins or not settings.terrain:
        return True
    leave = set(origins) | {cell}
    return any(
        not line_cover(start, cell, settings, {}, leave).total for start in origins
    )


def with_cover(target: dict, reading: CoverReading) -> dict:
    """Target as a roll against it reads it, with the map's cover among its
    visibility states (the most protective one counts,
    Combat/Effects/modifiers.py's `cover`): a copy, for reading only, or
    target itself with no cover to add."""
    state = reading.state
    if state is None:
        return target
    states = list(target.get("visibility_states") or [])
    if state in states:
        return target
    return {**target, "visibility_states": [*states, state]}
