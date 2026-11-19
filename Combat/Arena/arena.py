"""The battle map's state, with no Qt (Notes/combat-arena-plan.md, step 2):
the map's settings, where each combatant is and what it covers, how far
apart two creatures are, where a creature can move to, and where new tokens
go.

A combatant's place is on the combatant, as plain JSON (the plan's
Decision 4): `char["position"] = [col, row]`, its footprint's anchor cell,
and `char["moved_ft"]`, how far it has moved this turn. No "position" means
it isn't on the map. Every count goes through geometry's GridShape and
DistanceRule, never through the coordinates themselves.

The map's terrain (Combat/Arena/terrain.py, painted in the Map Painter:
Notes/map-painter-plan.md) is part of its settings: walls and blocking
objects can't be entered, Difficult Terrain costs extra, a step between
heights is a climb, and height counts into distances.

How a creature moves past others and over the ground can change by what it
has (movement_rules): a Movement on a badge (Freedom of Movement), from an
always-on feature (Halfling Nimbleness, Feature.movement) or a stat block's
trait (Incorporeal Movement, Swarm).

A Grappled creature names its grappler, `char["grappled_by"] = "Goblin"`
(step 22): the grappler drags it as it walks, each foot costing 1 extra
foot unless it's Tiny or two or more sizes smaller (Rules Glossary,
Grappled: Movable).

A creature moves by one of its speeds (step 26, Combat/Arena/speeds.py):
its Speed, or its Fly, Swim, Climb or Burrow Speed. Flying, the ground's
Difficult Terrain, water and heights cost nothing, and its altitude counts
into its distances; burrowing, it passes under creatures and Difficult
Terrain; swimming, it stays in the water. Water is swum (Rules Glossary,
Swimming): each foot costs 1 extra foot, 2 in Difficult Terrain, none by a
Swim Speed.
"""

from __future__ import annotations

import heapq
import re
from dataclasses import dataclass, field
from itertools import count
from typing import Iterable

from Combat.Arena.geometry import DEFAULT_RULE, Cell, DistanceRule, rule_named
from Combat.Arena.speeds import (  # noqa: F401 (TRAIT_MOVEMENT, movements: here too)
    BURROW,
    FLY,
    SWIM,
    TRAIT_MOVEMENT,
    altitude_ft,
    mode_of,
    movements,
    speed_of_mode,
)
from Combat.Arena.terrain import Terrain
from Combat.Effects.modifiers import (
    has_condition,
    size_in_use,
    speed_in_use,
)
from Combat.Effects.triggers import on_party_side
from Combat.Summons import owner_name
from Core.Definitions import Condition, CreatureSize
from Core.Weapons import WeaponProperty
from Model.Content.CombatModifiers import Movement
from Model.Content.StandardActions import DISENGAGE
from Model.Creatures.MonsterAbilities import stated_reach_and_range

POSITION_KEY = "position"
MOVED_KEY = "moved_ft"
# How many times it has taken the Dash action this turn (movement_ft).
DASHES_KEY = "dashes"
# Who has a Grappled creature grappled, by name (step 22).
GRAPPLER_KEY = "grappled_by"

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

# ArenaSettings.to_dict's key for `in_use`, there only when it's True.
IN_USE_KEY = "in_use"


@dataclass
class ArenaSettings:
    """The fight's map: `width` by `height` cells of `cell_ft` feet, counted
    by the distance rule named `rule` (geometry.RULES), with the `terrain`
    the Map Painter painted on it. The plan's Q1 suggestion gives the size:
    24 x 16 cells of 5 ft. for a fight with no map painted.

    `in_use`: the fight is being played on the map (a token was moved, or
    the painted map's starting cells placed someone), so its distances
    count in the rules that ask for one (Decision 29). Until then the
    tokens stand where place_new put them, which says nothing about the
    fight, and those rules stay notes for the GM."""

    width: int = 24
    height: int = 16
    cell_ft: int = 5
    rule: str = DEFAULT_RULE
    terrain: Terrain = field(default_factory=Terrain)
    in_use: bool = False

    @property
    def distance_rule(self) -> DistanceRule:
        return rule_named(self.rule)

    def to_dict(self) -> dict:
        """What the encounter log keeps under its "arena" key; "terrain"
        only when something is painted, "in_use" only when it is."""
        data: dict = {
            "width": self.width,
            "height": self.height,
            "cell_ft": self.cell_ft,
            "rule": self.rule,
        }
        if self.terrain:
            data["terrain"] = self.terrain.to_dict()
        if self.in_use:
            data[IN_USE_KEY] = True
        return data

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
            terrain=Terrain.from_dict(data.get("terrain")),
            in_use=bool(data.get(IN_USE_KEY, False)),
        )

    def copy(self) -> ArenaSettings:
        """A copy whose terrain can be painted without changing this one's."""
        return ArenaSettings.from_dict(self.to_dict())

    def on_map(self, cell: Cell) -> bool:
        return self.distance_rule.shape.in_bounds(cell, self.width, self.height)

    def standable(self, cell: Cell) -> bool:
        """On the map, and not a wall or a blocking object."""
        return self.on_map(cell) and not self.terrain.blocks(cell)

    def height_of(self, cells: Iterable[Cell]) -> int:
        """The ground height, in feet, under a footprint: its highest cell's,
        as a creature half on a ledge stands on it."""
        return max((self.terrain.height(cell) for cell in cells), default=0)

    def elevation(self, char: dict, cells: Iterable[Cell]) -> int:
        """How high char is with its footprint on `cells`: the ground's
        height there and the altitude it flies at (step 26)."""
        return self.height_of(cells) + altitude_ft(char)


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
    any of its cells. None when either isn't on the map. The ground's
    height under each counts too (the map-painter plan's Decision 5): a
    goblin on a 10-foot ledge next to you is 15 ft. away."""
    rule = settings.distance_rule
    cells_a, cells_b = footprint(a, rule), footprint(b, rule)
    if not cells_a or not cells_b:
        return None
    flat = min(rule.feet(x, y, settings.cell_ft) for x in cells_a for y in cells_b)
    rise = abs(settings.elevation(a, cells_a) - settings.elevation(b, cells_b))
    return rule.with_height(flat, rise)


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


def _in_force(char: dict, movement: Movement) -> bool:
    """Whether `movement` counts now: always, or one `after` an action only
    once char took it this turn (its Dash counted, its Disengage badge)."""
    if movement.after == "Dash":
        return dashes(char) > 0
    if movement.after == DISENGAGE:
        return DISENGAGE in (char.get("conditions") or ())
    return True


@dataclass(frozen=True)
class MovementRules:
    """What char's Movements in force add up to (movement_rules): each rule
    as Movement says it; the cheapest way to stand up when several give
    one."""

    past_larger: bool = False
    through_creatures: bool = False
    through_objects: bool = False
    shares_space: bool = False
    ignores_difficult: bool = False
    climbs: bool = False
    stands_up_ft: int | None = None
    sources: tuple[str, ...] = ()


def movement_rules(char: dict) -> MovementRules:
    """The rules for how char moves now, from every Movement it has that's
    in force (movements)."""
    found = [(source, m) for source, m in movements(char) if _in_force(char, m)]
    moves = [m for _, m in found]
    stands = [m.stands_up_ft for m in moves if m.stands_up_ft is not None]
    return MovementRules(
        past_larger=any(m.past_larger for m in moves),
        through_creatures=any(m.through_creatures for m in moves),
        through_objects=any(m.through_objects for m in moves),
        shares_space=any(m.shares_space for m in moves),
        ignores_difficult=any(m.ignores_difficult for m in moves),
        climbs=any(m.climbs for m in moves),
        stands_up_ft=min(stands) if stands else None,
        sources=tuple(dict.fromkeys(source for source, _ in found)),
    )


def can_pass_through(
    mover: dict, other: dict, rules: MovementRules | None = None
) -> bool:
    """Whether `mover` can move through `other`'s space (Player's Handbook,
    Moving Around Other Creatures): an ally's, an Incapacitated creature's,
    a Tiny creature's, or that of a creature two or more sizes larger or
    smaller. Or by what mover has (`rules`, its movement_rules): anyone's
    with Incorporeal Movement, a larger creature's with Halfling
    Nimbleness; and anyone can pass a Swarm, which others can occupy."""
    rules = rules if rules is not None else movement_rules(mover)
    return (
        _is_ally(mover, other)
        or _out_of_the_fight(other)
        or size_in_use(other) == CreatureSize.TINY
        or abs(_size_index(mover) - _size_index(other)) >= 2
        or rules.through_creatures
        or (rules.past_larger and _size_index(other) > _size_index(mover))
        or rules.shares_space
        or movement_rules(other).shares_space
    )


def can_share_space(
    mover: dict, other: dict, rules: MovementRules | None = None
) -> bool:
    """Whether `mover` can end a move in `other`'s space, which nobody
    willingly can (Moving Around Other Creatures) but a Swarm, in anyone's
    and anyone in its."""
    rules = rules if rules is not None else movement_rules(mover)
    return rules.shares_space or movement_rules(other).shares_space


def is_difficult_for(mover: dict, other: dict) -> bool:
    """Whether `other`'s space is Difficult Terrain to `mover` (Rules
    Glossary, Difficult Terrain: a creature that isn't Tiny or your ally)."""
    return not _is_ally(mover, other) and size_in_use(other) != CreatureSize.TINY


def has_climb_speed(char: dict) -> bool:
    """Whether char has a Climb Speed, which climbs at no extra cost."""
    climb = char.get("speed_climb_ft")
    return isinstance(climb, int) and not isinstance(climb, bool) and climb > 0


def reachable(
    char: dict, chars: Iterable[dict], settings: ArenaSettings, feet: int
) -> dict[Cell, int]:
    """Where char can end a move of up to `feet` feet, with what each costs
    (_walk_search)."""
    return _walk_search(char, chars, settings, feet)[0]


def walk_path(
    char: dict, chars: Iterable[dict], settings: ArenaSettings, to: Cell
) -> list[Cell] | None:
    """The cells char's anchor goes through on the cheapest walk to `to`,
    its own cell first and `to` last (step 23: the GM clicks where a walk
    ends, and this is the way it's taken to have gone); None when no walk
    gets there, or char isn't on the map."""
    ends, parents = _walk_search(char, chars, settings, _ANY_DISTANCE)
    if to not in ends:
        return None
    path = [to]
    while path[-1] in parents:
        path.append(parents[path[-1]])
    return path[::-1]


def _walk_search(
    char: dict, chars: Iterable[dict], settings: ArenaSettings, feet: int
) -> tuple[dict[Cell, int], dict[Cell, Cell]]:
    """Where char can end a move of up to `feet` feet, as its anchor cell,
    with what getting there costs: a uniform-cost search over the rule's
    steps. A step into another creature's space is Difficult Terrain unless
    it's Tiny or an ally, as is a step onto painted Difficult Terrain (1
    extra foot per foot, not cumulative), and Prone char crawls (1 extra
    foot per foot, both together 2); a step up or down a height difference
    climbs it, each foot costing 1 extra (2 in Difficult Terrain, none with
    a Climb Speed). It can't pass a creature it can't move through, a wall
    or a blocking object, can't end on anyone, and stays on the map. Char's
    own cell costs 0. Empty when char isn't on the map.

    What char has changes that (movement_rules): it passes whoever
    can_pass_through says, and ends where can_end_at would let it; walls and
    blocking objects are Difficult Terrain to it with `through_objects`;
    Difficult Terrain costs it nothing extra with `ignores_difficult`, and
    climbing nothing with `climbs`.

    So does the speed it moves by (mode_of, step 26): flying, the ground's
    Difficult Terrain (painted, water, furniture) and its heights cost
    nothing, only another creature's space is Difficult; burrowing, it
    passes under anyone (ending on nobody) and no Difficult Terrain or
    height costs anything; swimming, it goes only where water is. A step
    into water is swum otherwise (Rules Glossary, Swimming): 1 extra foot a
    foot, as well as Difficult Terrain's."""
    start = position(char)
    if start is None:
        return {}, {}
    chars = list(chars)
    rule, cell_ft = settings.distance_rule, settings.cell_ft
    rules = movement_rules(char)
    others = {
        cell: other
        for cell, other in occupied((c for c in chars if c is not char), rule).items()
    }
    crawling = has_condition(char, Condition.PRONE)
    # Dragging a creature it grapples: 1 extra foot a foot (Grappled: Movable).
    dragging = drags_at_a_cost(char, chars)
    mode = mode_of(char)
    flying, burrowing, swimming = mode == FLY, mode == BURROW, mode == SWIM
    climb_extra = 0 if has_climb_speed(char) or rules.climbs else 1
    terrain = settings.terrain
    seen: dict[Cell, tuple[bool, bool, int, bool] | None] = {}

    def entered(anchor: Cell) -> tuple[bool, bool, int, bool] | None:
        """Whether char's footprint at `anchor` can end a move there,
        whether it's Difficult Terrain there, the ground's height, and
        whether it swims there; None when it can't go there."""
        if anchor not in seen:
            seen[anchor] = _entering(anchor)
        return seen[anchor]

    def _entering(anchor: Cell) -> tuple[bool, bool, int, bool] | None:
        cells = footprint_at(char, anchor, rule)
        if not all(settings.on_map(cell) for cell in cells):
            return None
        wet = any(terrain.water(cell) for cell in cells)
        if swimming and not wet:
            return None
        inside = [cell for cell in cells if terrain.blocks(cell)]
        if inside and not rules.through_objects:
            return None
        met: list[dict] = []
        for cell in cells:
            other = others.get(cell)
            if other is not None and not any(other is m for m in met):
                if not burrowing and not can_pass_through(char, other, rules):
                    return None
                met.append(other)
        ground = not flying and any(terrain.difficult(c) for c in cells)
        difficult = (
            bool(inside)
            or ground
            or (not burrowing and any(is_difficult_for(char, o) for o in met))
        ) and not rules.ignores_difficult
        if burrowing:
            difficult = bool(inside) and not rules.ignores_difficult
        can_end = all(can_share_space(char, o, rules) for o in met)
        swims = wet and not flying and not swimming and not burrowing
        return can_end, difficult, settings.height_of(cells), swims

    start_height = settings.height_of(footprint_at(char, start, rule))
    best: dict[Cell, int] = {start: 0}
    # The cell each was reached from on its cheapest way (walk_path).
    parents: dict[Cell, Cell] = {}
    ends: dict[Cell, int] = {}
    tie = count()
    queue: list[tuple[int, int, Cell]] = [(0, next(tie), start)]
    while queue:
        cost, _, cell = heapq.heappop(queue)
        if cost > best.get(cell, cost):
            continue
        here = entered(cell) if cell != start else None
        if cell == start or (here is not None and here[0]):
            ends[cell] = cost
        height = here[2] if here is not None else start_height
        for step in rule.neighbours(cell):
            there = entered(step)
            if there is None:
                continue
            _, difficult, step_height, swims = there
            extra = int(crawling) + int(difficult) + int(dragging) + int(swims)
            climbed = abs(step_height - height) * (1 + climb_extra + int(difficult))
            if flying or burrowing:
                climbed = 0  # over the ledge, or under it
            new_cost = (
                cost + int(rule.step_cost(cell, step) * cell_ft * (1 + extra)) + climbed
            )
            if new_cost <= feet and new_cost < best.get(step, new_cost + 1):
                best[step] = new_cost
                parents[step] = cell
                heapq.heappush(queue, (new_cost, next(tie), step))
    return ends, parents


def grappler_of(char: dict, chars: Iterable[dict]) -> dict | None:
    """Who has char Grappled, among `chars`: the one it names (GRAPPLER_KEY)
    while it's Grappled; None when it isn't, or the grappler isn't known
    (Grappled given by hand with no source) or has left the fight."""
    name = char.get(GRAPPLER_KEY)
    if not name or not has_condition(char, Condition.GRAPPLED):
        return None
    return next((c for c in chars if c is not char and c.get("name") == name), None)


def grappled_by(grappler: dict, chars: Iterable[dict]) -> list[dict]:
    """The creatures among `chars` that `grappler` has Grappled."""
    chars = list(chars)
    return [c for c in chars if grappler_of(c, chars) is grappler]


def drag_costs_extra(grappler: dict, grappled: dict) -> bool:
    """Whether dragging `grappled` costs `grappler` 1 extra foot a foot
    (Rules Glossary, Grappled: Movable): unless it's Tiny or two or more
    sizes smaller."""
    if size_in_use(grappled) == CreatureSize.TINY:
        return False
    return _size_index(grappler) - _size_index(grappled) < 2


def drags_at_a_cost(grappler: dict, chars: Iterable[dict]) -> bool:
    """Whether `grappler` walking now drags someone at a cost: one it has
    Grappled, on the map, not Tiny or two sizes smaller. Several cost no
    more than one (each foot costs 1 extra foot, whoever is dragged)."""
    return any(
        position(held) is not None and drag_costs_extra(grappler, held)
        for held in grappled_by(grappler, chars)
    )


def grapple_range_ft(grappler: dict) -> int:
    """How far apart a grapple holds (Rules Glossary, Grappling: it ends
    "if the distance between the Grappled target and the grappler exceeds
    the grapple's range"): the grappler's reach, as the attack or Unarmed
    Strike that grappled was made within it (Decision 34)."""
    return reach_ft(grappler)


def fits_at(
    char: dict, anchor: Cell, chars: Iterable[dict], settings: ArenaSettings
) -> bool:
    """Whether char can stand with its anchor at `anchor`: on the map, on
    no wall or blocking object, and on nobody else's cells. Where a token
    is put; can_end_at says where a move can end."""
    rule = settings.distance_rule
    taken = occupied((c for c in chars if c is not char), rule)
    cells = footprint_at(char, anchor, rule)
    return all(settings.standable(cell) and cell not in taken for cell in cells)


def can_end_at(
    char: dict, anchor: Cell, chars: Iterable[dict], settings: ArenaSettings
) -> bool:
    """Whether a move of char's can end with its anchor at `anchor`: where
    it fits (fits_at), or where what it has lets it stay
    (movement_rules): inside a wall or an object with `through_objects`
    (Incorporeal Movement, which hurts as its turn ends there), in another
    creature's space when either is a Swarm."""
    rule = settings.distance_rule
    rules = movement_rules(char)
    taken = occupied((c for c in chars if c is not char), rule)
    for cell in footprint_at(char, anchor, rule):
        if not settings.on_map(cell):
            return False
        if settings.terrain.blocks(cell) and not rules.through_objects:
            return False
        other = taken.get(cell)
        if other is not None and not can_share_space(char, other, rules):
            return False
    return True


def stand_up_ft(char: dict) -> int | None:
    """What righting itself from Prone costs char, in feet of movement
    (Rules Glossary, Prone: "half your Speed (round down)"), or a feature's
    less (Athlete's Hop Up: 5 feet); None when it has no speed as a number.
    A Speed of 0 can't right itself, which is the caller's to say."""
    speed = walking_speed_ft(char)
    own = movement_rules(char).stands_up_ft
    if speed is None:
        return own
    return speed // 2 if own is None else min(speed // 2, own)


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


def dashes(char: dict) -> int:
    """How many times char has taken the Dash action this turn."""
    return int(char.get(DASHES_KEY, 0))


def movement_ft(char: dict) -> int | None:
    """How far char can move this turn by the speed it moves by (mode_of:
    its Speed, or its Fly Speed, ...), and its Speed more for each Dash it
    has taken (Rules Glossary, Dash: "The increase equals your Speed after
    applying any modifiers"; a creature with no Speed, its speed's). What
    it moved already counts against a new speed (Speed: "subtract the
    distance already moved from the new speed": remaining_ft). None when it
    has no speed as a number."""
    speed = speed_of_mode(char)
    if speed is None:
        speed = walking_speed_ft(char)
    if speed is None:
        return None
    return speed + dashes(char) * (walking_speed_ft(char) or speed)


def remaining_ft(char: dict) -> int:
    """How far char can still move this turn: its movement (its walking
    speed in use, with its Dashes) less what it has moved (0 with no speed)."""
    return max((movement_ft(char) or 0) - int(char.get(MOVED_KEY, 0)), 0)


_REACH = re.compile(r"\breach (\d+) ft\.", re.IGNORECASE)
_STAT_BLOCK_SECTIONS = ("actions", "bonus_actions", "reactions", "legendary_actions")


def reach_ft(char: dict) -> int:
    """How far char's melee attacks reach (Rules Glossary, Reach: 5 feet,
    10 with a Reach weapon): a monster's longest reach in its stat block
    (a MeleeAttack's `reach_ft`, or a freeform ability's "reach 10 ft."), a
    player's 10 feet with a Reach weapon; else 5 feet."""
    reaches = [5]
    for key in _STAT_BLOCK_SECTIONS:
        for ability in char.get(key) or ():
            stated = stated_reach_and_range(ability)
            if stated is not None:
                if stated[0] is not None:
                    reaches.append(int(stated[0]))
                continue
            text = (
                ability.get("description", "")
                if isinstance(ability, dict)
                else getattr(ability, "description", "")
            )
            reaches += [int(feet) for feet in _REACH.findall(str(text))]
    for weapon in char.get("_weapons_objects") or ():
        if WeaponProperty.REACH in (getattr(weapon, "properties", None) or ()):
            reaches.append(10)
    return max(reaches)


def _in_reach_along(
    mover: dict, cells: list[Cell], other: dict, reach: int, settings: ArenaSettings
) -> list[bool]:
    """Whether mover is within `reach` feet of `other` at each of `cells`
    (its anchor on the way)."""
    inside = []
    for cell in cells:
        feet = distance_ft(
            dict(mover, **{POSITION_KEY: cell.to_list()}), other, settings
        )
        inside.append(feet is not None and feet <= reach)
    return inside


def _can_react(mover: dict, other: dict) -> bool:
    """Whether `other` could take a Reaction against mover now: not on its
    side, not down or Incapacitated, its Reaction not used since its turn
    began."""
    if other is mover or _is_ally(mover, other) or _out_of_the_fight(other):
        return False
    return (other.get("action_uses") or {}).get("Reaction", 0) == 0


def opportunity_attackers(
    mover: dict,
    start: Cell,
    chars: Iterable[dict],
    settings: ArenaSettings,
    path: list[Cell] | None = None,
) -> list[dict]:
    """Who can make an Opportunity Attack as mover's walk from `start` to
    where it stands now takes it out of their reach (Rules Glossary,
    Opportunity Attacks): each creature not on its side, on the map, not
    down or Incapacitated, its Reaction not used since its turn began, that
    had mover in its reach at one cell of the walk and not at the next.
    `path` is the walk's cells (walk_path, `start` first), so a walk that
    passes through a reach, or leaves it and comes back, is caught (step
    23); without it only the walk's two ends are known."""
    end = position(mover)
    cells = list(path) if path else [start] + ([end] if end is not None else [])
    found = []
    for other in chars:
        if not _can_react(mover, other):
            continue
        inside = _in_reach_along(mover, cells, other, reach_ft(other), settings)
        if any(was and not now for was, now in zip(inside, inside[1:])):
            found.append(other)
    return found


POLEARM_MASTER = "Polearm Master"
# The weapons Polearm Master's Reactive Strike is made with, by class name
# (a magic Spear's class comes from Spear's; a Javelin shares Spear's
# family, SpearMedium, but not its class), besides any Heavy Reach one.
_POLEARMS = ("Quarterstaff", "Spear")


def _polearm_reach_ft(char: dict) -> int | None:
    """The reach char has with a weapon it holds that Polearm Master's
    Reactive Strike is made with (a Quarterstaff, a Spear, or one with the
    Heavy and Reach properties), when it has the feat; None otherwise. A
    player's weapons are taken to be held, as the picker lists them."""
    feats = [getattr(f, "name", "") for f in char.get("_feature_objects") or ()]
    if POLEARM_MASTER not in feats:
        return None
    reaches = []
    for weapon in char.get("_weapons_objects") or ():
        properties = getattr(weapon, "properties", None) or ()
        named = any(kind.__name__ in _POLEARMS for kind in type(weapon).__mro__)
        heavy_reach = (
            WeaponProperty.HEAVY in properties and WeaponProperty.REACH in properties
        )
        if named or heavy_reach:
            reaches.append(10 if WeaponProperty.REACH in properties else 5)
    return max(reaches) if reaches else None


def reactive_strikers(
    mover: dict,
    path: list[Cell],
    chars: Iterable[dict],
    settings: ArenaSettings,
) -> list[dict]:
    """Who can make Polearm Master's Reactive Strike on mover, whose walk
    along `path` entered the reach it has with its polearm ("a creature
    that enters the reach you have with that weapon"): each that could react
    now (as an Opportunity Attack's attacker), had mover outside that reach
    at one cell of the walk and inside it at the next. Disengage doesn't
    stop it: it isn't an Opportunity Attack."""
    found = []
    for other in chars:
        reach = _polearm_reach_ft(other)
        if reach is None or not _can_react(mover, other):
            continue
        inside = _in_reach_along(mover, path, other, reach, settings)
        if any(now and not was for was, now in zip(inside, inside[1:])):
            found.append(other)
    return found


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


def distance_to_cell_ft(char: dict, cell: Cell, settings: ArenaSettings) -> int | None:
    """How far `cell` is from char, from char's nearest cell (Decision 8),
    the ground's height under both counted in; None when char isn't on the
    map."""
    rule = settings.distance_rule
    cells = footprint(char, rule)
    if not cells:
        return None
    flat = min(rule.feet(own, cell, settings.cell_ft) for own in cells)
    rise = abs(settings.elevation(char, cells) - settings.terrain.height(cell))
    return rule.with_height(flat, rise)
