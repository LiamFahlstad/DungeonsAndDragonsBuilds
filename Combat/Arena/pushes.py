"""Where a push or a pull leaves a creature on the battle map (arena plan,
step 21): Thunderwave's 10 feet away, a Shove's 5, the Push mastery's "up
to 10 feet straight away from yourself", Thorn Whip's pull "up to 10 feet
closer to you". Qt-free, like the rest of Combat/Arena.

"Straight away" on a grid (Decision 32): each 5 feet is one step to a
neighbouring cell that puts the creature one step farther from its pusher
(nearer, for a pull), by the map's distance rule, and of those the one
nearest the straight line from the pusher's middle through the creature's
middle as it started. So a push along a row stays on the row, and a
diagonal one goes as a staircase along the diagonal. It stops short of
what it can't be moved into: the map's edge, a wall or an object that
blocks movement, or anyone else's space (where the move couldn't end:
`can_end_at`, so an incorporeal creature goes into a wall and a Swarm into
a space). A pull stops next to its puller.

Nothing here moves a token: the window does, as a Push move (no movement
spent, no Opportunity Attack; arena_mixin._move_combatant)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from Combat.Arena.arena import (
    ArenaSettings,
    can_end_at,
    footprint,
    footprint_at,
    occupied,
    position,
)
from Combat.Arena.geometry import Cell, DistanceRule
from Combat.Effects.modifiers import size_in_use
from Model.Content.CombatEffect import CombatPush
from Model.Content.CombatTriggers import size_fits


@dataclass(frozen=True)
class PushResult:
    """Where a push leaves its target: its anchor `to` (its own cell when
    it can't be moved at all), how far that is, and what stopped it short
    ("" when it went the whole way)."""

    to: Cell
    feet: int
    stopped_by: str = ""


def too_big(target: dict, push: CombatPush) -> bool:
    """Whether the target is larger than the push moves ("if it is Large or
    smaller"); a size not known counts as small enough, for the GM."""
    if push.largest is None:
        return False
    return size_fits(size_in_use(target), push.largest) is False


def _middle(cells: Iterable[Cell], rule: DistanceRule) -> tuple[float, float]:
    """Where the middle of a creature's cells is, in the shape's own units
    (a cell of size 1), for the line it's pushed along."""
    points = [rule.shape.center(cell, 1.0) for cell in cells]
    return (
        sum(x for x, _ in points) / len(points),
        sum(y for _, y in points) / len(points),
    )


def _off_line(
    point: tuple[float, float],
    start: tuple[float, float],
    direction: tuple[float, float],
) -> float:
    """How far `point` is from the line through `start` along `direction`."""
    dx, dy = point[0] - start[0], point[1] - start[1]
    length = (direction[0] ** 2 + direction[1] ** 2) ** 0.5
    return abs(dx * direction[1] - dy * direction[0]) / length


def _apart(a: Iterable[Cell], b: Iterable[Cell], rule: DistanceRule) -> float:
    """Steps between two creatures' nearest cells."""
    b = list(b)
    return min(rule.steps(x, y) for x in a for y in b)


def _what_stops(
    target: dict, anchor: Cell, chars: Iterable[dict], settings: ArenaSettings
) -> str:
    """What's where the target couldn't be pushed to, for the log line."""
    rule = settings.distance_rule
    taken = occupied((c for c in chars if c is not target), rule)
    for cell in footprint_at(target, anchor, rule):
        if not settings.on_map(cell):
            return "the map's edge"
        if settings.terrain.blocks(cell):
            return "a wall or an object"
        if cell in taken:
            return f"{taken[cell]['name']}'s space"
    return "something in the way"


def push_destination(
    target: dict,
    pusher: dict,
    push: CombatPush,
    chars: Iterable[dict],
    settings: ArenaSettings,
) -> PushResult | None:
    """Where `push` from `pusher` leaves `target` (see the module
    docstring); None when it can't be worked out: either is off the map,
    or they share a space (a Swarm), so there is no "away"."""
    chars = list(chars)
    rule = settings.distance_rule
    start = position(target)
    source_cells = footprint(pusher, rule)
    if start is None or not source_cells:
        return None
    target_cells = footprint(target, rule)
    if set(source_cells) & set(target_cells):
        return None
    origin = _middle(source_cells, rule)
    middle = _middle(target_cells, rule)
    direction = (middle[0] - origin[0], middle[1] - origin[1])
    sign = -1 if push.toward else 1
    anchor, feet = start, 0
    steps = push.feet // settings.cell_ft
    for _ in range(steps):
        here = _apart(source_cells, footprint_at(target, anchor, rule), rule)
        candidates = []
        for cell in rule.neighbours(anchor):
            cells = footprint_at(target, cell, rule)
            apart = _apart(source_cells, cells, rule)
            if apart != here + sign or apart < 1:
                continue
            candidates.append(
                (_off_line(_middle(cells, rule), origin, direction), cell)
            )
        if not candidates:
            # A pull that's already next to its puller.
            return PushResult(anchor, feet)
        best = min(candidates, key=lambda pair: pair[0])[1]
        if not can_end_at(target, best, chars, settings):
            return PushResult(anchor, feet, _what_stops(target, best, chars, settings))
        anchor = best
        feet += settings.cell_ft
    return PushResult(anchor, feet)


def push_order(
    targets: Iterable[dict], pusher: dict, push: CombatPush, settings: ArenaSettings
) -> list[dict]:
    """The targets in the order to move them: for a push the farthest from
    the pusher first, so a nearer one isn't stopped by one that's about to
    move off (Thunderwave's front row behind its back row); for a pull the
    nearest first. Off the map last."""
    rule = settings.distance_rule
    source = footprint(pusher, rule)

    def key(target: dict) -> tuple[bool, float]:
        cells = footprint(target, rule)
        if not cells or not source:
            return (True, 0)
        apart = _apart(source, cells, rule)
        return (False, apart if push.toward else -apart)

    return sorted(targets, key=key)
