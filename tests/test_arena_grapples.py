"""Grapples on the battle map, on plain combatant dicts
(Notes/combat-arena-plan.md step 22; Combat/Arena/arena.py and
grapples.py).

Rules Glossary, Grappled: "The grappler can drag or carry you when it
moves, but every foot of movement costs it 1 extra foot unless you are Tiny
or two or more sizes smaller than it." Grappling: the condition ends "if
the distance between the Grappled target and the grappler exceeds the
grapple's range"."""

from Combat.Arena.arena import (
    GRAPPLER_KEY,
    ArenaSettings,
    drag_costs_extra,
    drags_at_a_cost,
    grapple_range_ft,
    grappled_by,
    grappler_of,
    reachable,
)
from Combat.Arena.geometry import Cell
from Combat.Arena.grapples import dragged_to, stretched
from Combat.Arena.terrain import WALL, Spot


def _char(name: str, col: int | None, row: int = 5, **extra) -> dict:
    char = {"name": name, "conditions": [], "hp": 10, "speed": 30, **extra}
    if col is not None:
        char["position"] = [col, row]
    return char


def _held(name: str, col: int | None, grappler: str, row: int = 5, **extra) -> dict:
    return _char(
        name, col, row, conditions=["Grappled"], **{GRAPPLER_KEY: grappler}, **extra
    )


def test_who_grapples_whom_is_read_from_the_grappled_creature():
    edmund = _char("Edmund", 5)
    goblin = _held("Goblin", 6, "Edmund")
    loose = _char("Orc", 7, **{GRAPPLER_KEY: "Edmund"})  # Grappled came off
    chars = [edmund, goblin, loose]
    assert grappler_of(goblin, chars) is edmund
    assert grappler_of(loose, chars) is None
    assert grappled_by(edmund, chars) == [goblin]
    assert grappler_of(_held("Kobold", 4, "Nobody"), chars) is None


def test_dragging_costs_1_extra_foot_a_foot_unless_tiny_or_two_sizes_smaller():
    edmund = _char("Edmund", 5, size="Medium")
    assert drag_costs_extra(edmund, _char("Goblin", 6, size="Small"))
    assert drag_costs_extra(edmund, _char("Tiger", 6, size="Large"))
    assert not drag_costs_extra(edmund, _char("Rat", 6, size="Tiny"))
    ogre = _char("Ogre", 5, size="Large")
    assert drag_costs_extra(ogre, _char("Edmund", 7, size="Medium"))
    assert not drag_costs_extra(ogre, _char("Goblin", 7, size="Small"))
    giant = _char("Giant", 5, size="Huge")
    assert not drag_costs_extra(giant, _char("Goblin", 8, size="Small"))


def test_a_grappler_dragging_reaches_half_as_far():
    edmund = _char("Edmund", 10)
    goblin = _held("Goblin", 11, "Edmund")
    settings = ArenaSettings()
    reach = reachable(edmund, [edmund, goblin], settings, 30)
    assert drags_at_a_cost(edmund, [edmund, goblin])
    assert reach[Cell(7, 5)] == 30, "15 ft. walked, 30 ft. spent"
    assert Cell(6, 5) not in reach
    off_map = _held("Goblin", None, "Edmund")
    assert not drags_at_a_cost(edmund, [edmund, off_map]), "only one on the map"


def test_the_dragged_creature_keeps_its_place_beside_the_grappler():
    settings = ArenaSettings()
    edmund = _char("Edmund", 7)  # walked from 10 to 7
    goblin = _held("Goblin", 11, "Edmund")
    assert dragged_to(goblin, edmund, Cell(10, 5), [edmund, goblin], settings) == (
        Cell(8, 5)
    )


def test_the_dragged_creature_goes_round_a_wall_within_the_grapple():
    settings = ArenaSettings()
    settings.terrain.put(Cell(8, 5), Spot(ground=WALL))
    edmund = _char("Edmund", 7)
    goblin = _held("Goblin", 11, "Edmund")
    to = dragged_to(goblin, edmund, Cell(10, 5), [edmund, goblin], settings)
    assert to in (Cell(7, 4), Cell(7, 6)), "next to Edmund, not in the wall"


def test_a_grapple_stretched_past_its_range_is_found():
    settings = ArenaSettings()
    edmund = _char("Edmund", 5)
    goblin = _held("Goblin", 7, "Edmund")
    [gap] = stretched([edmund, goblin], settings)
    assert (gap.held, gap.grappler, gap.feet, gap.range_ft) == (
        goblin,
        edmund,
        10,
        5,
    )
    goblin["position"] = [6, 5]
    assert stretched([edmund, goblin], settings) == []
    goblin.pop("position")
    assert stretched([edmund, goblin], settings) == [], "off the map: not measured"


def test_a_grapple_reaches_as_far_as_the_grapplers_reach():
    whip = _char(
        "Kraken",
        5,
        actions=[{"name": "Tentacle", "description": "Melee Attack: reach 10 ft."}],
    )
    assert grapple_range_ft(whip) == 10
    goblin = _held("Goblin", 7, "Kraken")
    assert stretched([whip, goblin], ArenaSettings()) == []
