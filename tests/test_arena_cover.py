"""Cover from the battle map, with no Qt (Notes/combat-arena-plan.md, step
19). Expected results come from the rules:

- Rules Glossary, Cover: Half Cover "+2 bonus to AC and Dexterity saving
  throws", Three-Quarters Cover +5, Total Cover "can't be targeted
  directly"; "If behind more than one degree of cover, a target benefits
  only from the most protective degree."
- Player's Handbook, Cover: a low wall, large furniture or "a creature,
  whether that creature is an enemy or a friend" gives Half Cover.
- Rules Glossary, Area of Effect: a location no unblocked straight line
  from the point of origin reaches isn't in the area.

The map's own choices (Decision 30): the line between two cells' middles,
the least-covered line between the two creatures, a corner squeezed past
covered as its less protective side, the ends' own cells giving none."""

from typing import Any

from Combat.Arena.arena import ArenaSettings
from Combat.Arena.areas import AreaOfEffect, AreaShape, area_cells, point_of_origin
from Combat.Arena.cover import (
    NO_COVER_READING,
    cover_between,
    cover_from,
    reaches,
    with_cover,
)
from Combat.Arena.geometry import SQUARE_GRID, Cell
from Combat.Arena.lasting import area_record, record_origin
from Combat.Arena.terrain import (
    HALF,
    NO_COVER,
    THREE_QUARTERS,
    TOTAL,
    WALL,
    MapObject,
    Spot,
)
from Combat.Fight.effect_options import _spell_named, read_effect_text
from Combat.Effects.modifiers import armor_class
from Combat.Effects.roll_plans import save_plan

BARREL = Spot(thing=MapObject("Barrel", blocks=True, cover=HALF))
PILLAR = Spot(thing=MapObject("Pillar", blocks=True, cover=THREE_QUARTERS))
DOOR = Spot(thing=MapObject("Door", blocks=True, cover=TOTAL))
TABLE = Spot(thing=MapObject("Table", difficult=True, cover=HALF))
STONE = Spot(ground=WALL)


def _monster(name: str, at, size: str = "Medium", **keys: Any) -> dict:
    char = {"name": name, "size": size, "hp": 7, "speed_ground_ft": 30, **keys}
    char["position"] = list(at)
    return char


def _player(name: str, at, **keys: Any) -> dict:
    char = {"name": name, "_is_player": True, "size": "Medium", "hp": 20}
    char.update(keys, position=list(at))
    return char


def _settings(painted: dict[tuple[int, int], Spot] | None = None) -> ArenaSettings:
    settings = ArenaSettings()
    for (col, row), spot in (painted or {}).items():
        settings.terrain.put(Cell(col, row), spot)
    return settings


def _cover(settings, attacker, target, *others):
    return cover_from(attacker, target, [attacker, target, *others], settings)


# ---------------------------------------------------------------------------
# The line


def test_a_straight_line_crosses_the_cells_between_its_ends():
    assert SQUARE_GRID.crossed(Cell(0, 0), Cell(3, 0)) == [(Cell(1, 0),), (Cell(2, 0),)]
    assert SQUARE_GRID.crossed(Cell(0, 0), Cell(1, 0)) == []


def test_a_line_through_a_corner_squeezes_between_two_cells():
    """From A1's middle to C3's the line passes B2's middle and two corners."""
    assert SQUARE_GRID.crossed(Cell(0, 0), Cell(2, 2)) == [
        (Cell(1, 0), Cell(0, 1)),
        (Cell(1, 1),),
        (Cell(2, 1), Cell(1, 2)),
    ]


def test_a_shallow_line_steps_across_before_it_steps_down():
    assert SQUARE_GRID.crossed(Cell(0, 0), Cell(4, 1)) == [
        (Cell(1, 0),),
        (Cell(2, 0),),
        (Cell(2, 1),),
        (Cell(3, 1),),
    ]


# ---------------------------------------------------------------------------
# What gives cover


def test_open_ground_gives_none():
    archer, goblin = _player("Archer", (0, 0)), _monster("Goblin", (4, 0))
    assert _cover(_settings(), archer, goblin) == NO_COVER_READING


def test_a_barrel_between_gives_half_cover():
    archer, goblin = _player("Archer", (0, 0)), _monster("Goblin", (4, 0))
    reading = _cover(_settings({(2, 0): BARREL}), archer, goblin)
    assert (reading.degree, reading.by) == (HALF, "Barrel at C1")
    assert reading.state == "Half Cover"
    assert reading.text == "Half Cover from Barrel at C1: +2 AC and DEX saves"


def test_a_pillar_gives_three_quarters_cover():
    archer, goblin = _player("Archer", (0, 0)), _monster("Goblin", (4, 0))
    reading = _cover(_settings({(2, 0): PILLAR}), archer, goblin)
    assert reading.state == "Three-Quarters Cover"


def test_a_wall_and_a_closed_door_are_total_cover():
    archer, goblin = _player("Archer", (0, 0)), _monster("Goblin", (4, 0))
    wall = _cover(_settings({(3, 0): STONE}), archer, goblin)
    door = _cover(_settings({(1, 0): DOOR}), archer, goblin)
    assert (wall.total, wall.by) == (True, "Wall at D1")
    assert (door.total, door.by) == (True, "Door at B1")


def test_only_the_most_protective_degree_counts():
    archer, goblin = _player("Archer", (0, 0)), _monster("Goblin", (5, 0))
    reading = _cover(_settings({(1, 0): BARREL, (3, 0): PILLAR}), archer, goblin)
    assert (reading.degree, reading.by) == (THREE_QUARTERS, "Pillar at D1")


def test_a_creature_in_the_way_gives_half_cover_friend_or_foe():
    archer, goblin = _player("Archer", (0, 0)), _monster("Goblin", (4, 0))
    friend = _player("Friend", (2, 0))
    foe = _monster("Other goblin", (2, 0))
    assert _cover(_settings(), archer, goblin, friend).by == "Friend"
    assert _cover(_settings(), archer, goblin, foe).degree == HALF


def test_a_creature_down_at_0_hp_gives_none():
    archer, goblin = _player("Archer", (0, 0)), _monster("Goblin", (4, 0))
    fallen = _monster("Fallen", (2, 0), hp=0)
    assert not _cover(_settings(), archer, goblin, fallen)


def test_what_stands_on_either_creatures_own_cell_gives_none():
    """A goblin standing on a table isn't behind it."""
    archer, goblin = _player("Archer", (0, 0)), _monster("Goblin", (4, 0))
    assert not _cover(_settings({(4, 0): TABLE, (0, 0): TABLE}), archer, goblin)


def test_beside_the_line_gives_none():
    archer, goblin = _player("Archer", (0, 0)), _monster("Goblin", (4, 0))
    assert not _cover(_settings({(2, 1): STONE, (2, 2): STONE}), archer, goblin)


def test_a_corner_squeezed_past_is_covered_as_its_open_side():
    """Diagonally past one wall's corner: the line has open ground beside it."""
    archer, goblin = _player("Archer", (0, 0)), _monster("Goblin", (2, 2))
    assert not _cover(_settings({(1, 0): STONE}), archer, goblin)


def test_a_gap_between_two_walls_corners_is_total_cover():
    archer, goblin = _player("Archer", (0, 0)), _monster("Goblin", (2, 2))
    walls = _settings({(1, 0): STONE, (0, 1): STONE})
    assert _cover(walls, archer, goblin).total


def test_a_large_attacker_picks_its_least_covered_line():
    """The archer at F2: the lines from the ogre's top row cross the wall
    at D1, its bottom row's run along row 2."""
    ogre = _monster("Ogre", (0, 0), size="Large")
    archer = _player("Archer", (5, 1))
    walled = _settings({(3, 0): STONE})
    assert not cover_from(ogre, archer, [ogre, archer], walled)
    both = _settings({(3, 0): STONE, (3, 1): STONE})
    assert cover_from(ogre, archer, [ogre, archer], both).total


def test_off_the_map_there_is_no_cover():
    archer = _player("Archer", (0, 0))
    goblin = {"name": "Goblin", "size": "Medium", "hp": 7}
    assert not _cover(_settings({(2, 0): STONE}), archer, goblin)


def test_cover_from_a_point_of_origin_leaves_the_caster_out():
    """A Fireball's cell, the caster standing between it and the goblin."""
    caster, goblin = _player("Caster", (2, 0)), _monster("Goblin", (4, 0))
    chars = [caster, goblin]
    assert cover_between([Cell(0, 0)], goblin, chars, _settings()).by == "Caster"
    assert not cover_between([Cell(0, 0)], goblin, chars, _settings(), [caster])


# ---------------------------------------------------------------------------
# What the cover does to a roll


def test_with_cover_adds_the_maps_cover_to_a_copy():
    goblin = _monster("Goblin", (4, 0), visibility_states=[])
    reading = _cover(_settings({(2, 0): BARREL}), _player("Archer", (0, 0)), goblin)
    seen = with_cover(goblin, reading)
    assert armor_class(seen, 15) == 17
    assert goblin["visibility_states"] == []
    assert armor_class(goblin, 15) == 15
    assert with_cover(goblin, NO_COVER_READING) is goblin


def test_a_dexterity_save_gets_the_cover_bonus():
    goblin = _monster("Goblin", (4, 0))
    reading = _cover(_settings({(2, 0): PILLAR}), _player("Archer", (0, 0)), goblin)
    plan = save_plan(with_cover(goblin, reading), "DEX", "Neutral")
    assert ("Three-Quarters Cover", "5") in plan.bonuses
    assert save_plan(with_cover(goblin, reading), "WIS", "Neutral").bonuses == ()


def test_the_targets_own_cover_counts_if_it_is_more_protective():
    goblin = _monster("Goblin", (4, 0), visibility_states=["Three-Quarters Cover"])
    reading = _cover(_settings({(2, 0): BARREL}), _player("Archer", (0, 0)), goblin)
    assert armor_class(with_cover(goblin, reading), 15) == 20


def test_total_cover_adds_nothing_to_the_ac():
    """It can't be targeted at all: the window warns, the AC stays."""
    goblin = _monster("Goblin", (4, 0))
    reading = _cover(_settings({(2, 0): STONE}), _player("Archer", (0, 0)), goblin)
    assert armor_class(with_cover(goblin, reading), 15) == 15


def ignores_cover(text: str) -> bool:
    """What the text reading (a spell or feature without combat effects)
    makes of it."""
    return read_effect_text(text).ignores_cover


def test_sacred_flame_and_the_bypass_cover_feats_ignore_cover():
    sacred_flame = _spell_named("Sacred Flame").combat_effects()
    assert [effect.ignores_cover for effect in sacred_flame] == [True]
    assert ignores_cover(
        "The target gains no benefit from Half Cover or Three-Quarters Cover"
        " for this save."
    )
    assert ignores_cover(
        "Your attack rolls for spells ignore Half Cover and Three-Quarters Cover."
    )
    assert not ignores_cover("A target with Half Cover has a +2 bonus.")
    assert NO_COVER_READING.degree == NO_COVER


# ---------------------------------------------------------------------------
# Areas stop at Total Cover


FIREBALL = AreaOfEffect(AreaShape.SPHERE, 20)


def test_a_sphere_doesnt_reach_behind_a_wall():
    """A wall along column E, from row 1 to row 9: the Sphere's point is in
    column C, so column F and beyond are behind it (the wall's own cells
    are reached, and nobody stands on them)."""
    walls = _settings({(4, row): STONE for row in range(0, 9)})
    cells = area_cells(FIREBALL, None, Cell(2, 4), walls)
    assert Cell(5, 4) not in cells
    assert Cell(3, 4) in cells
    open_cells = area_cells(FIREBALL, None, Cell(2, 4), _settings())
    assert Cell(5, 4) in open_cells
    assert cells == {c for c in open_cells if c.col <= 4}


def test_a_barrel_doesnt_stop_an_area():
    barrel = _settings({(3, 4): BARREL})
    assert Cell(4, 4) in area_cells(FIREBALL, None, Cell(2, 4), barrel)


def test_a_cone_from_the_source_stops_at_a_wall():
    caster = _player("Caster", (0, 4))
    cone = AreaOfEffect(AreaShape.CONE, 15)
    walled = _settings({(1, 4): STONE})
    open_cells = area_cells(cone, caster, Cell(3, 4), _settings())
    assert Cell(3, 4) in open_cells
    assert Cell(3, 4) not in area_cells(cone, caster, Cell(3, 4), walled)


def test_the_point_of_origin_is_the_aim_or_the_source():
    caster = _player("Caster", (0, 4))
    settings = _settings()
    assert point_of_origin(FIREBALL, caster, Cell(5, 5), settings) == [Cell(5, 5)]
    cone = AreaOfEffect(AreaShape.CONE, 15)
    assert point_of_origin(cone, caster, Cell(5, 5), settings) == [Cell(0, 4)]
    assert reaches([Cell(0, 0)], Cell(9, 9), settings)


def test_a_kept_records_origin_is_its_aim_unless_it_starts_at_the_source():
    caster = _player("Caster", (0, 4))
    settings = _settings()
    sphere = area_record(FIREBALL, caster, Cell(6, 4), settings)
    cone = area_record(AreaOfEffect(AreaShape.CONE, 15), caster, Cell(3, 4), settings)
    assert record_origin(sphere) == [Cell(6, 4)]
    assert record_origin(cone) is None
