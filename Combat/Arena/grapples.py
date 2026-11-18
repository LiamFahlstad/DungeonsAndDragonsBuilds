"""Grapples on the battle map (Notes/combat-arena-plan.md, step 22), Qt-free.

Rules Glossary, Grappled: "Movable. The grappler can drag or carry you
when it moves, but every foot of movement costs it 1 extra foot unless you
are Tiny or two or more sizes smaller than it." Grappling: "The condition
also ends if the grappler has the Incapacitated condition or if the
distance between the Grappled target and the grappler exceeds the
grapple's range."

Who grapples whom is on the grappled creature (arena.GRAPPLER_KEY); the
extra cost of a walk is counted by arena.reachable. Here: where a dragged
creature ends up as its grappler walks (`dragged_to`, Decision 34), and
which grapples a move has stretched past their range (`stretched`)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from Combat.Arena.arena import (
    POSITION_KEY,
    ArenaSettings,
    can_end_at,
    distance_ft,
    grapple_range_ft,
    grappler_of,
    position,
)
from Combat.Arena.geometry import Cell


def _within_range(
    held: dict, anchor: Cell, grappler: dict, settings: ArenaSettings
) -> bool:
    placed = dict(held, **{POSITION_KEY: anchor.to_list()})
    feet = distance_ft(placed, grappler, settings)
    return feet is not None and feet <= grapple_range_ft(grappler)


def dragged_to(
    held: dict,
    grappler: dict,
    grappler_from: Cell,
    chars: Iterable[dict],
    settings: ArenaSettings,
) -> Cell | None:
    """Where `held` goes as `grappler` (already moved) walks from
    `grappler_from`: the same way and as far, keeping its place beside the
    grappler, or, when that cell won't take it (a wall, someone, the map's
    edge), the nearest one to it that does and is within the grapple's
    range. None when either isn't on the map or nowhere fits, which the
    caller leaves to the grapple's range to end."""
    chars = list(chars)
    start, now = position(held), position(grappler)
    if start is None or now is None:
        return None
    rule = settings.distance_rule
    wanted = rule.shape.shifted(start, grappler_from, now)
    frontier = [wanted]
    seen = {wanted}
    while frontier:
        for cell in frontier:
            if (
                settings.on_map(cell)
                and can_end_at(held, cell, chars, settings)
                and _within_range(held, cell, grappler, settings)
            ):
                return cell
        following = []
        for cell in frontier:
            for step in rule.neighbours(cell):
                if step not in seen and settings.on_map(step):
                    seen.add(step)
                    following.append(step)
        frontier = following
    return None


@dataclass(frozen=True)
class Stretched:
    """A grapple a move has pulled apart: `held` is `feet` from its
    `grappler`, past the grapple's `range_ft`."""

    held: dict
    grappler: dict
    feet: int
    range_ft: int


def stretched(chars: Iterable[dict], settings: ArenaSettings) -> list[Stretched]:
    """Each grapple whose two are farther apart than its range now; one
    with either off the map isn't measured."""
    chars = list(chars)
    found = []
    for held in chars:
        grappler = grappler_of(held, chars)
        if grappler is None:
            continue
        feet = distance_ft(held, grappler, settings)
        reach = grapple_range_ft(grappler)
        if feet is not None and feet > reach:
            found.append(Stretched(held, grappler, feet, reach))
    return found
