"""An encounter's painted map, with no Qt (Notes/map-painter-plan.md): the
map's settings and terrain, and where its combatants start, kept in
Combat/Campaigns/<Campaign>/Maps/<encounter id>.json and written by the
Map Painter.

A fight that starts reads it: its map becomes the fight's own (the log's
"arena" key, which keeps it from then on, so a fight continued later plays
on the map it started on), and whoever has a starting cell starts there.
An encounter with no map file plays on the default empty map, the party on
the left and everyone else on the right, as before."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from Combat.Arena.arena import (
    POSITION_KEY,
    ArenaSettings,
    fits_at,
    nearest_free,
    position,
)
from Combat.Arena.geometry import Cell
from Combat.LogFiles import read_json, write_json

MAPS_DIR = "Maps"
ARENA_KEY = "arena"
START_KEY = "start"


@dataclass
class MapDesign:
    """A painted map: its `settings` (size, distance rule, terrain) and the
    anchor cell each combatant starts on, by name."""

    settings: ArenaSettings = field(default_factory=ArenaSettings)
    starts: dict[str, Cell] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            ARENA_KEY: self.settings.to_dict(),
            START_KEY: {name: cell.to_list() for name, cell in self.starts.items()},
        }

    @classmethod
    def from_dict(cls, data: dict | None) -> MapDesign:
        data = data or {}
        starts = {}
        for name, at in (data.get(START_KEY) or {}).items():
            try:
                starts[str(name)] = Cell.of(at)
            except (TypeError, ValueError):
                continue
        return cls(ArenaSettings.from_dict(data.get(ARENA_KEY)), starts)

    def copy(self) -> MapDesign:
        return MapDesign.from_dict(self.to_dict())

    def cropped(self) -> MapDesign:
        """Without the terrain and starting cells past the map's edge: what's
        saved after the map was made smaller."""
        settings = self.settings.copy()
        settings.terrain = settings.terrain.within(settings.on_map)
        starts = {n: c for n, c in self.starts.items() if settings.on_map(c)}
        return MapDesign(settings, starts)


def map_path(combat_log_dir: Path, encounter_id: str) -> Path:
    """Where an encounter's map is kept: Maps/ beside the campaign's
    CombatLogs/."""
    return Path(combat_log_dir).parent / MAPS_DIR / f"{encounter_id}.json"


def read_map(path: Path) -> MapDesign | None:
    """The map painted at `path`; None when there's none (or it's empty)."""
    path = Path(path)
    if not path.exists():
        return None
    data = read_json(path)
    return MapDesign.from_dict(data) if data else None


def write_map(path: Path, design: MapDesign):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(path, design.cropped().to_dict())


def place_at_starts(
    chars: Iterable[dict], starts: dict[str, Cell], settings: ArenaSettings
) -> list[dict]:
    """Put each of `chars` without a position that has a starting cell on
    it, or on the nearest free cell when someone (or a wall) is there now.
    Returns those placed; the rest are place_new's."""
    chars = list(chars)
    placed = []
    for char in chars:
        start = starts.get(char.get("name", ""))
        if start is None or position(char) is not None:
            continue
        if fits_at(char, start, chars, settings):
            anchor: Cell | None = start
        else:
            anchor = nearest_free(char, [start], chars, settings)
        if anchor is not None:
            char[POSITION_KEY] = anchor.to_list()
            placed.append(char)
    return placed
