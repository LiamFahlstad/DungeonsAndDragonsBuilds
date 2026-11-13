"""The battle map's state, with no Qt (Notes/combat-arena-plan.md, step 2):
the map's settings, where each combatant is and what it covers, how far
apart two creatures are, where a creature can move to, and where new tokens
go.

A combatant's place is on the combatant, as plain JSON (the plan's
Decision 4): `char["position"] = [col, row]`, its footprint's anchor cell,
and `char["moved_ft"]`, how far it has moved this turn. No "position" means
it isn't on the map. Every count goes through geometry's GridShape and
DistanceRule, never through the coordinates themselves.
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass
from itertools import count
from typing import Iterable

from Combat.Arena.geometry import DEFAULT_RULE, Cell, DistanceRule, rule_named
from Combat.Effects.modifiers import has_condition, size_in_use, speed_in_use
from Combat.Effects.triggers import on_party_side
from Combat.Summons import owner_name
from Core.Definitions import Condition, CreatureSize

POSITION_KEY = "position"
MOVED_KEY = "moved_ft"

# How many cells across a creature of each size covers on a 5-foot grid
# (Rules Glossary, Creature Size: Tiny 2.5 ft., Small and Medium 5 ft.,
# Large 10 ft., Huge 15 ft., Gargantuan 20 ft.). A Tiny creature takes a
# whole cell on the map; several Tiny creatures in one cell is Later.
SIZE_CELLS = {
    CreatureSize.TINY: 1,
    CreatureSize.SMALL: 1,
    CreatureSize.MEDIUM: 1,
    CreatureSize.LARGE: 2,
    CreatureSize.HUGE: 3,
    CreatureSize.GARGANTUAN: 4,
}
_SIZE_ORDER = list(CreatureSize)


@dataclass
class ArenaSettings:
    """The fight's map: `width` by `height` cells of `cell_ft` feet, counted
    by the distance rule named `rule` (geometry.RULES). The plan's Q1
    suggestion gives the size: 24 x 16 cells of 5 ft. for every fight."""

    width: int = 24
    height: int = 16
    cell_ft: int = 5
    rule: str = DEFAULT_RULE

    @property
    def distance_rule(self) -> DistanceRule:
        return rule_named(self.rule)

    def to_dict(self) -> dict:
        """What the encounter log keeps under its "arena" key."""
        return {
            "width": self.width,
            "height": self.height,
            "cell_ft": self.cell_ft,
            "rule": self.rule,
        }

    @classmethod
    def from_dict(cls, data: dict | None) -> ArenaSettings:
        """The settings an encounter log kept; the defaults for anything it
        doesn't have, as an older log has none."""
        data = data or {}
        default = cls()
        return cls(
            width=int(data.get("width", default.width)),
            height=int(data.get("height", default.height)),
            cell_ft=int(data.get("cell_ft", default.cell_ft)),
            rule=str(data.get("rule", default.rule)),
        )

    def on_map(self, cell: Cell) -> bool:
        return self.distance_rule.shape.in_bounds(cell, self.width, self.height)


def position(char: dict) -> Cell | None:
    """Char's anchor cell, or None when it isn't on the map."""
    data = char.get(POSITION_KEY)
    return None if data is None else Cell.of(data)


def size_cells(char: dict) -> int:
    """How many cells across char covers, by its size in use (an Enlarged
    Medium creature covers 2); 1 when its size isn't known."""
    size = size_in_use(char)
    return SIZE_CELLS.get(size, 1) if size is not None else 1


def footprint_at(char: dict, anchor: Cell, rule: DistanceRule) -> list[Cell]:
    """The cells char would cover with its anchor at `anchor`."""
    return rule.shape.footprint(anchor, size_cells(char))


def footprint(char: dict, rule: DistanceRule) -> list[Cell]:
    """The cells char covers now; none when it isn't on the map."""
    anchor = position(char)
    return [] if anchor is None else footprint_at(char, anchor, rule)


def occupied(chars: Iterable[dict], rule: DistanceRule) -> dict[Cell, dict]:
    """Each covered cell, with whoever covers it."""
    return {cell: char for char in chars for cell in footprint(char, rule)}


def distance_ft(a: dict, b: dict, settings: ArenaSettings) -> int | None:
    """How far apart two creatures are, in feet, between their nearest cells
    (the plan's Decision 8): a Large creature is 5 ft. from anything next to
    any of its cells. None when either isn't on the map."""
    rule = settings.distance_rule
    cells_a, cells_b = footprint(a, rule), footprint(b, rule)
    if not cells_a or not cells_b:
        return None
    return min(rule.feet(x, y, settings.cell_ft) for x in cells_a for y in cells_b)


def walking_speed_ft(char: dict) -> int | None:
    """The speed char's reach on the map comes from, in use (Haste doubles
    it, Grappled makes it 0): its walking speed (a monster's
    speed_ground_ft, a player's speed), or with neither its highest other
    speed (the plan's Q7). None when it has no speed as a number."""
    for key in ("speed_ground_ft", "speed"):
        stored = char.get(key)
        if isinstance(stored, int) and not isinstance(stored, bool):
            return speed_in_use(char, stored)
    others = [
        char[key]
        for key in ("speed_fly_ft", "speed_climb_ft")
        if isinstance(char.get(key), int)
    ]
    return speed_in_use(char, max(others)) if others else None


def _size_index(char: dict) -> int:
    size = size_in_use(char) or CreatureSize.MEDIUM
    return _SIZE_ORDER.index(size)


def _is_ally(a: dict, b: dict) -> bool:
    return on_party_side(a) == on_party_side(b)


def _out_of_the_fight(char: dict) -> bool:
    """Incapacitated, or down at 0 HP (the plan's Q9): it blocks nobody."""
    hp = char.get("hp")
    return has_condition(char, Condition.INCAPACITATED) or (
        isinstance(hp, (int, float)) and hp <= 0
    )


def can_pass_through(mover: dict, other: dict) -> bool:
    """Whether `mover` can move through `other`'s space (Player's Handbook,
    Moving Around Other Creatures): an ally's, an Incapacitated creature's,
    a Tiny creature's, or that of a creature two or more sizes larger or
    smaller."""
    return (
        _is_ally(mover, other)
        or _out_of_the_fight(other)
        or size_in_use(other) == CreatureSize.TINY
        or abs(_size_index(mover) - _size_index(other)) >= 2
    )


def is_difficult_for(mover: dict, other: dict) -> bool:
    """Whether `other`'s space is Difficult Terrain to `mover` (Rules
    Glossary, Difficult Terrain: a creature that isn't Tiny or your ally)."""
    return not _is_ally(mover, other) and size_in_use(other) != CreatureSize.TINY


def reachable(
    char: dict, chars: Iterable[dict], settings: ArenaSettings, feet: int
) -> dict[Cell, int]:
    """Where char can end a move of up to `feet` feet, as its anchor cell,
    with what getting there costs: a uniform-cost search over the rule's
    steps. A step into another creature's space is Difficult Terrain unless
    it's Tiny or an ally (1 extra foot per foot), and Prone char crawls (1
    extra foot per foot, both together 2); it can't pass a creature it
    can't move through, can't end on anyone, and stays on the map. Char's
    own cell costs 0. Empty when char isn't on the map."""
    start = position(char)
    if start is None:
        return {}
    rule, cell_ft = settings.distance_rule, settings.cell_ft
    others = {
        cell: other
        for cell, other in occupied((c for c in chars if c is not char), rule).items()
    }
    crawling = has_condition(char, Condition.PRONE)

    def entered(anchor: Cell) -> list[dict] | None:
        """Who the footprint at `anchor` overlaps; None when it can't go there."""
        cells = footprint_at(char, anchor, rule)
        if not all(settings.on_map(cell) for cell in cells):
            return None
        met = []
        for cell in cells:
            other = others.get(cell)
            if other is not None and not any(other is m for m in met):
                if not can_pass_through(char, other):
                    return None
                met.append(other)
        return met

    best: dict[Cell, int] = {start: 0}
    ends: dict[Cell, int] = {}
    tie = count()
    queue: list[tuple[int, int, Cell]] = [(0, next(tie), start)]
    while queue:
        cost, _, cell = heapq.heappop(queue)
        if cost > best.get(cell, cost):
            continue
        met = entered(cell) if cell != start else []
        if not met:
            ends[cell] = cost
        for step in rule.neighbours(cell):
            met_there = entered(step)
            if met_there is None:
                continue
            extra = int(crawling) + int(
                any(is_difficult_for(char, o) for o in met_there)
            )
            new_cost = cost + int(rule.step_cost(cell, step) * cell_ft * (1 + extra))
            if new_cost <= feet and new_cost < best.get(step, new_cost + 1):
                best[step] = new_cost
                heapq.heappush(queue, (new_cost, next(tie), step))
    return ends


def fits_at(
    char: dict, anchor: Cell, chars: Iterable[dict], settings: ArenaSettings
) -> bool:
    """Whether char can stand with its anchor at `anchor`: on the map and on
    nobody else's cells."""
    rule = settings.distance_rule
    taken = occupied((c for c in chars if c is not char), rule)
    cells = footprint_at(char, anchor, rule)
    return all(settings.on_map(cell) and cell not in taken for cell in cells)


def nearest_free(
    char: dict, near: Iterable[Cell], chars: Iterable[dict], settings: ArenaSettings
) -> Cell | None:
    """The anchor nearest to the cells `near` (by the rule's steps) where char
    fits, searching outward from them; None when the map is full. The cells
    in `near` themselves count when char fits there."""
    chars = list(chars)
    rule = settings.distance_rule
    frontier = [cell for cell in near if settings.on_map(cell)]
    seen = set(frontier)
    while frontier:
        for cell in frontier:
            if fits_at(char, cell, chars, settings):
                return cell
        following = []
        for cell in frontier:
            for step in rule.neighbours(cell):
                if step not in seen and settings.on_map(step):
                    seen.add(step)
                    following.append(step)
        frontier = following
    return None


def place_beside(
    char: dict, owner: dict, chars: Iterable[dict], settings: ArenaSettings
) -> Cell | None:
    """The first free anchor next to `owner` (a summon beside its caster);
    None when the owner isn't on the map or there's no room."""
    rule = settings.distance_rule
    own = footprint(owner, rule)
    if not own:
        return None
    around = [step for cell in own for step in rule.neighbours(cell) if step not in own]
    return nearest_free(char, dict.fromkeys(around), chars, settings)


def place_new(chars: Iterable[dict], settings: ArenaSettings) -> list[dict]:
    """Give everyone without a position a starting cell (the plan's Q1): the
    party's side along the left edge, everyone else along the right, from
    the middle row outward and then inward column by column, never on
    anyone. Sets each one's "position" and returns those placed."""
    chars = list(chars)
    shape = settings.distance_rule.shape
    placed = []
    for left in (True, False):
        order = shape.from_edge(settings.width, settings.height, left)
        for char in chars:
            if position(char) is not None or on_party_side(char) != left:
                continue
            for cell in order:
                anchor = _anchor_from_edge(char, cell, left, settings)
                if anchor is not None and fits_at(char, anchor, chars, settings):
                    char[POSITION_KEY] = anchor.to_list()
                    placed.append(char)
                    break
    return placed


def _anchor_from_edge(
    char: dict, cell: Cell, left: bool, settings: ArenaSettings
) -> Cell | None:
    """The anchor that puts char's footprint against the edge it starts on:
    `cell` itself from the left, and from the right the anchor whose
    footprint ends at `cell`'s column."""
    if left:
        return cell
    across = size_cells(char)
    anchor = settings.distance_rule.shape.offset(cell, 1 - across, 0)
    return anchor if settings.on_map(anchor) else None


def place_summons(new: Iterable[dict], chars: Iterable[dict], settings: ArenaSettings):
    """Put each of the summons `new` beside its owner among `chars`, when the
    owner is on the map and there's room; the rest stay off it."""
    chars = list(chars)
    for char in new:
        owner = next((c for c in chars if c.get("name") == owner_name(char)), None)
        if owner is None or position(char) is not None:
            continue
        cell = place_beside(char, owner, chars + [char], settings)
        if cell is not None:
            char[POSITION_KEY] = cell.to_list()
            chars.append(char)


def remaining_ft(char: dict) -> int:
    """How far char can still move this turn: its walking speed in use less
    what it has moved (0 with no speed)."""
    speed = walking_speed_ft(char)
    return max((speed or 0) - int(char.get(MOVED_KEY, 0)), 0)


# A walk no map is long enough to need: reachable's limit when it's a cost
# that's wanted, not a reach.
_ANY_DISTANCE = 1_000_000


def move_cost(
    char: dict, chars: Iterable[dict], settings: ArenaSettings, to: Cell
) -> int | None:
    """What walking char to anchor `to` costs, in feet, by the cheapest way
    it can go (around whoever it can't pass, crawling while Prone); None
    when no walk gets there, or char isn't on the map."""
    return reachable(char, chars, settings, _ANY_DISTANCE).get(to)


def straight_ft(char: dict, to: Cell, settings: ArenaSettings) -> int | None:
    """How far anchor `to` is from char's anchor by the rule, ignoring
    whoever is in the way (a teleport, or a walk that can't be made); None
    when char isn't on the map."""
    start = position(char)
    if start is None:
        return None
    return settings.distance_rule.feet(start, to, settings.cell_ft)
