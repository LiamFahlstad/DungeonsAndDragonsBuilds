"""What a battle map is made of besides its grid, with no Qt
(Notes/map-painter-plan.md): each cell's ground (open, a wall, Difficult
Terrain, water), its height, its light, and an object standing on it (a
table, a barrel, a campfire), as the Map Painter paints them.

The rules the arena counts from it (Combat/Arena/arena.py):

- Nobody enters or ends a move on a wall, or on an object that blocks
  movement (a barrel, a pillar).
- Difficult Terrain and furniture make a step cost 1 extra foot a foot
  (Rules Glossary, Difficult Terrain: "isn't cumulative", so a creature's
  space on top of it costs no more).
- Water is swum (Rules Glossary, Swimming, step 26 of the arena plan): 1
  extra foot a foot, 2 in Difficult Terrain (an enemy's space in it), none
  for a creature swimming by its Swim Speed or flying over it.
- A step between two heights is a climb (Rules Glossary, Climbing: each foot
  costs 1 extra foot, 2 extra in Difficult Terrain, none with a Climb
  Speed), and height counts into the distance between two creatures.
- Dim light is Lightly Obscured and Darkness Heavily Obscured (Rules
  Glossary, Dim Light and Darkness): shown, not rolled.
- An object's cover (Rules Glossary, Cover) is shown on the hover, and
  counted between two creatures (Combat/Arena/cover.py); a wall is Total
  Cover. A hazard (a campfire, a trap) is a reminder to whoever enters it or
  starts a turn on it.

Everything is plain JSON in the encounter's map file and the fight's log
(`Terrain.to_dict`), and only cells that differ from open, level, brightly
lit ground are kept. Nothing here does arithmetic on a cell's coordinates
(the arena plan's Decision 3)."""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from Combat.Arena.geometry import Cell

# A cell's ground.
OPEN = "open"
WALL = "wall"
DIFFICULT = "difficult"
WATER = "water"
GROUNDS = {
    OPEN: "Open ground",
    WALL: "Wall",
    DIFFICULT: "Difficult Terrain",
    WATER: "Water (swimming)",
}

# A cell's light (Rules Glossary, Vision and Senses).
BRIGHT = "bright"
DIM = "dim"
DARK = "dark"
LIGHTS = {
    BRIGHT: "Bright Light",
    DIM: "Dim Light (Lightly Obscured)",
    DARK: "Darkness (Heavily Obscured)",
}
OBSCURED = {DIM: "Lightly Obscured", DARK: "Heavily Obscured"}

# An object's cover (Rules Glossary, Cover).
NO_COVER = "none"
HALF = "half"
THREE_QUARTERS = "three_quarters"
TOTAL = "total"
COVERS = {
    NO_COVER: "No cover",
    HALF: "Half Cover",
    THREE_QUARTERS: "Three-Quarters Cover",
    TOTAL: "Total Cover",
}

# How far the painter's heights go, in feet, either way.
MAX_HEIGHT_FT = 500


@dataclass(frozen=True)
class MapObject:
    """Something standing on a cell: its `name`, whether it `blocks`
    movement (nobody can be on its cell), makes the cell `difficult`
    terrain (furniture), the `cover` it gives, and whether it's a `hazard`
    (a reminder on entering it, or starting a turn on it)."""

    name: str
    blocks: bool = False
    difficult: bool = False
    cover: str = NO_COVER
    hazard: bool = False

    def to_dict(self) -> dict:
        data: dict = {"name": self.name}
        if self.blocks:
            data["blocks"] = True
        if self.difficult:
            data["difficult"] = True
        if self.cover != NO_COVER:
            data["cover"] = self.cover
        if self.hazard:
            data["hazard"] = True
        return data

    @classmethod
    def from_dict(cls, data: dict) -> MapObject:
        cover = str(data.get("cover", NO_COVER))
        return cls(
            name=str(data.get("name", "Object")),
            blocks=bool(data.get("blocks", False)),
            difficult=bool(data.get("difficult", False)),
            cover=cover if cover in COVERS else NO_COVER,
            hazard=bool(data.get("hazard", False)),
        )

    def describe(self) -> str:
        """ "Barrel (blocks movement, Half Cover)"."""
        notes = []
        if self.blocks:
            notes.append("blocks movement")
        if self.difficult:
            notes.append("Difficult Terrain")
        if self.cover != NO_COVER:
            notes.append(COVERS[self.cover])
        if self.hazard:
            notes.append("hazard")
        return self.name + (f" ({', '.join(notes)})" if notes else "")


# What the painter offers to put down, each changeable before it's painted.
# Cover as the Player's Handbook's examples give it: a low wall or large
# furniture half, a thick tree trunk three-quarters.
OBJECT_PRESETS: tuple[MapObject, ...] = (
    MapObject("Table", difficult=True, cover=HALF),
    MapObject("Low wall", difficult=True, cover=HALF),
    MapObject("Barrel", blocks=True, cover=HALF),
    MapObject("Crate", blocks=True, cover=HALF),
    MapObject("Pillar", blocks=True, cover=THREE_QUARTERS),
    MapObject("Tree", blocks=True, cover=THREE_QUARTERS),
    MapObject("Boulder", blocks=True, cover=THREE_QUARTERS),
    MapObject("Statue", blocks=True, cover=THREE_QUARTERS),
    MapObject("Door", blocks=True, cover=TOTAL),
    MapObject("Rubble", difficult=True),
    MapObject("Bushes", difficult=True),
    MapObject("Campfire", hazard=True),
    MapObject("Trap", hazard=True),
)


@dataclass(frozen=True)
class Spot:
    """What one cell is: its ground, height in feet, light and object."""

    ground: str = OPEN
    height_ft: int = 0
    light: str = BRIGHT
    thing: MapObject | None = None

    @property
    def plain(self) -> bool:
        """Open, level, brightly lit and empty: not kept."""
        return self == PLAIN

    def to_dict(self, cell: Cell) -> dict:
        data: dict = {"at": cell.to_list()}
        if self.ground != OPEN:
            data["ground"] = self.ground
        if self.height_ft:
            data["height"] = self.height_ft
        if self.light != BRIGHT:
            data["light"] = self.light
        if self.thing is not None:
            data["object"] = self.thing.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> Spot:
        ground, light = data.get("ground", OPEN), data.get("light", BRIGHT)
        thing = data.get("object")
        return cls(
            ground=ground if ground in GROUNDS else OPEN,
            height_ft=_clamped_height(data.get("height", 0)),
            light=light if light in LIGHTS else BRIGHT,
            thing=MapObject.from_dict(thing) if isinstance(thing, dict) else None,
        )


PLAIN = Spot()


def _clamped_height(value) -> int:
    try:
        feet = int(value)
    except (TypeError, ValueError):
        return 0
    return max(-MAX_HEIGHT_FT, min(MAX_HEIGHT_FT, feet))


@dataclass
class Terrain:
    """Every cell that isn't plain, by cell. A cell not in `cells` is open,
    level, brightly lit ground with nothing on it."""

    cells: dict[Cell, Spot] = field(default_factory=dict)

    def __bool__(self) -> bool:
        return bool(self.cells)

    def at(self, cell: Cell) -> Spot:
        return self.cells.get(cell, PLAIN)

    def put(self, cell: Cell, spot: Spot):
        """Make `cell` what `spot` says; a plain one is forgotten."""
        if spot.plain:
            self.cells.pop(cell, None)
        else:
            self.cells[cell] = spot

    def change(self, cell: Cell, **changes) -> bool:
        """Change some of `cell`'s Spot fields (ground=, height_ft=, light=,
        thing=); whether anything changed."""
        before = self.at(cell)
        after = replace(before, **changes)
        if after == before:
            return False
        self.put(cell, after)
        return True

    def blocks(self, cell: Cell) -> bool:
        """Nobody can enter it: a wall, or an object that blocks movement."""
        spot = self.at(cell)
        return spot.ground == WALL or (spot.thing is not None and spot.thing.blocks)

    def difficult(self, cell: Cell) -> bool:
        """Difficult Terrain: its ground, or furniture on it. Water isn't:
        it's swum (water)."""
        spot = self.at(cell)
        return spot.ground == DIFFICULT or (
            spot.thing is not None and spot.thing.difficult
        )

    def water(self, cell: Cell) -> bool:
        """Water to swim in (Rules Glossary, Swimming)."""
        return self.at(cell).ground == WATER

    def height(self, cell: Cell) -> int:
        return self.at(cell).height_ft

    def hazard(self, cell: Cell) -> MapObject | None:
        thing = self.at(cell).thing
        return thing if thing is not None and thing.hazard else None

    def describe(self, cell: Cell) -> list[str]:
        """What the hover says of the cell, besides its distance: ["Wall"],
        ["Difficult Terrain", "10 ft. up", "Darkness (Heavily Obscured)",
        "Barrel (blocks movement, Half Cover)"]; nothing for plain ground."""
        spot = self.at(cell)
        parts = []
        if spot.ground != OPEN:
            parts.append(GROUNDS[spot.ground])
        if spot.height_ft:
            parts.append(height_text(spot.height_ft))
        if spot.light != BRIGHT:
            parts.append(LIGHTS[spot.light])
        if spot.thing is not None:
            parts.append(spot.thing.describe())
        return parts

    def within(self, on_map) -> Terrain:
        """Only the cells `on_map(cell)` keeps: what's left after the map
        shrinks."""
        return Terrain({cell: s for cell, s in self.cells.items() if on_map(cell)})

    def to_dict(self) -> dict:
        """{"cells": [{"at": [col, row], "ground": "wall", ...}, ...]}, row
        by row."""
        order = sorted(self.cells, key=lambda c: (c.row, c.col))
        return {"cells": [self.cells[c].to_dict(c) for c in order]}

    @classmethod
    def from_dict(cls, data: dict | None) -> Terrain:
        terrain = cls()
        for entry in (data or {}).get("cells", []):
            if not isinstance(entry, dict) or "at" not in entry:
                continue
            terrain.put(Cell.of(entry["at"]), Spot.from_dict(entry))
        return terrain


def height_text(feet: int) -> str:
    """ "10 ft. up", "5 ft. down"."""
    return f"{abs(feet)} ft. {'up' if feet > 0 else 'down'}"
