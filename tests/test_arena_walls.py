"""Walls on the battle map, with no Qt (Notes/combat-arena-plan.md, step
25): the Wall shape (Combat/Arena/areas.py) read from the wall spells' own
text, its cells straight or in a ring, its sides and Wall of Fire's
damaging side; and what a kept wall is as terrain while it lasts
(Combat/Arena/lasting.py: Wall of Force blocks movement and is Total Cover,
Blade Barrier is Three-Quarters Cover and Difficult Terrain), laid over the
painted map without changing it. Also DI-096: a light's radius isn't an
area, and Flaming Sphere's is the 5 feet around it."""

from typing import Any

import pytest

from Combat.Arena.areas import (
    AreaOfEffect,
    AreaShape,
    area_cells,
    damaging_side_ft,
    parse_area,
    side_cells,
    side_name,
    side_of,
    wall_cells,
    wall_end,
    wall_ring_ft,
)
from Combat.Arena.arena import ArenaSettings, reachable
from Combat.Arena.cover import cover_from
from Combat.Arena.geometry import Cell
from Combat.Arena.lasting import (
    AREA_KEY,
    AreaPrompt,
    ENDS,
    ENTERS,
    area_record,
    area_timing,
    areas_beside,
    lasting_areas,
    record_origin,
    wall_terrain,
    with_kept_walls,
)
from Combat.Arena.terrain import HALF, THREE_QUARTERS, TOTAL, WALL, MapObject, Spot
from Combat.CombatUIQt.effect_options import _spell_named

SETTINGS = ArenaSettings()  # 24 x 16 cells of 5 ft., Manhattan
WALL_OF_FIRE = AreaOfEffect(AreaShape.WALL, 60, 1)
RING = AreaOfEffect(AreaShape.WALL, 20, 1, ring=True)


def _text(name: str) -> str:
    spell = _spell_named(name)
    assert spell is not None, name
    return spell.description


def _creature(name: str, at, **keys: Any) -> dict:
    char = {"name": name, "size": "Medium", "hp": 7, "speed_ground_ft": 30, **keys}
    char["position"] = list(at)
    return char


def _caster_with(record: dict, at=(0, 0), name: str = "Wall of Force") -> dict:
    caster = _creature("Clover", at)
    caster["active_spells"] = [
        {"name": name, "concentration": True, "applied": [], AREA_KEY: record}
    ]
    return caster


# ---------------------------------------------------------------------------
# Reading the walls from their text


@pytest.mark.parametrize(
    "spell, length, thick",
    [
        ("Wall of Fire", 60, 1),  # "up to 60 feet long, 20 feet high, and 1 foot thick"
        ("Blade Barrier", 100, 5),  # "a straight wall up to 100 feet long"
        ("Wall of Thorns", 60, 5),
        ("Wall of Force", 100, 1),  # "ten 10-foot-by-10-foot panels"
    ],
)
def test_the_wall_spells_read_as_walls(spell, length, thick):
    assert parse_area(_text(spell)) == AreaOfEffect(AreaShape.WALL, length, thick)


@pytest.mark.parametrize(
    "spell, across",
    [
        ("Wall of Fire", 20),  # "a ringed wall up to 20 feet in diameter"
        ("Blade Barrier", 60),
        ("Wall of Thorns", 20),  # "a circle that has a 20-foot diameter"
        ("Wall of Force", 20),  # "a globe with a radius of up to 10 feet"
    ],
)
def test_each_reads_its_ring(spell, across):
    assert wall_ring_ft(_text(spell)) == across


def test_only_wall_of_fire_has_a_damaging_side():
    assert damaging_side_ft(_text("Wall of Fire")) == 10
    for spell in ("Wall of Force", "Blade Barrier", "Wall of Thorns"):
        assert damaging_side_ft(_text(spell)) is None


def test_wall_of_fire_acts_as_a_creature_enters_it_or_ends_its_turn():
    timing = area_timing(_text("Wall of Fire"))
    assert ENTERS in timing and ENDS in timing


def test_a_lights_radius_is_no_area():
    """DI-096: Flaming Sphere "sheds Bright Light in a 20-foot radius"."""
    assert parse_area(_text("Light")) is None
    assert parse_area("It sheds Bright Light in a 20-foot radius.") is None


def test_flaming_sphere_reaches_5_feet_around_it():
    """DI-096: "Any creature that ends its turn within 5 feet of the
    sphere": its cell and the cells beside it."""
    area = parse_area(_text("Flaming Sphere"))
    assert area == AreaOfEffect(AreaShape.SPHERE, 5)
    cells = area_cells(AreaOfEffect(AreaShape.SPHERE, 5), None, Cell(6, 2), SETTINGS)
    assert cells == {Cell(6, 2), Cell(5, 2), Cell(7, 2), Cell(6, 1), Cell(6, 3)}


# ---------------------------------------------------------------------------
# The cells


def test_a_straight_wall_goes_from_end_to_end():
    assert wall_cells(WALL_OF_FIRE, Cell(2, 5), Cell(5, 5), SETTINGS) == {
        Cell(c, 5) for c in range(2, 6)
    }
    assert wall_cells(WALL_OF_FIRE, Cell(2, 5), None, SETTINGS) == {Cell(2, 5)}


def test_it_stops_at_its_length():
    """60 feet along a row: 12 cells, however far the other end is."""
    cells = wall_cells(WALL_OF_FIRE, Cell(0, 5), Cell(20, 5), SETTINGS)
    assert cells == {Cell(c, 5) for c in range(12)}
    assert wall_end(WALL_OF_FIRE, Cell(0, 5), Cell(20, 5), SETTINGS) == Cell(11, 5)
    assert wall_end(WALL_OF_FIRE, Cell(0, 5), Cell(5, 5), SETTINGS) == Cell(5, 5)


def test_a_diagonal_wall_leaves_no_gap_to_walk_through():
    force = AreaOfEffect(AreaShape.WALL, 100, 1)
    # Across the map's top-left corner, A7 to G1: 60 ft. by the map's rule.
    record = area_record(
        force, None, Cell(0, 6), SETTINGS, about=_text("Wall of Force"), end=Cell(6, 0)
    )
    caster = _caster_with(record, at=(23, 0))
    walker = _creature("Goblin", (1, 1), speed_ground_ft=200)
    settings = with_kept_walls(SETTINGS, [caster, walker])
    reach = reachable(walker, [caster, walker], settings, 200)
    assert reach and all(cell.col + cell.row < 5 for cell in reach), "shut in"


def test_a_ring_is_closed_around_its_middle():
    cells = wall_cells(RING, Cell(10, 8), None, SETTINGS)
    # 10 ft. from the middle by the map's rule, all round.
    assert len(cells) == 8 and Cell(10, 8) not in cells
    assert {Cell(12, 8), Cell(8, 8), Cell(10, 6), Cell(10, 10), Cell(11, 9)} <= cells


def test_a_wall_has_no_point_of_origin_to_be_cut_off_from():
    """A painted wall doesn't stop a wall cast across it, as it would a
    Fireball's spread."""
    settings = ArenaSettings()
    settings.terrain.put(Cell(4, 5), Spot(ground=WALL))
    assert Cell(6, 5) in area_cells(
        WALL_OF_FIRE, None, Cell(2, 5), settings, Cell(8, 5)
    )


# ---------------------------------------------------------------------------
# Sides


def test_a_straight_walls_sides_and_their_names():
    aim, end = Cell(2, 5), Cell(8, 5)
    south = side_of(WALL_OF_FIRE, aim, end, Cell(4, 7), SETTINGS)
    north = side_of(WALL_OF_FIRE, aim, end, Cell(4, 3), SETTINGS)
    assert {south, north} == {1, -1}
    assert side_of(WALL_OF_FIRE, aim, end, Cell(10, 5), SETTINGS) == 0, "on its line"
    assert side_name(WALL_OF_FIRE, aim, end, south) == "south"
    assert side_name(WALL_OF_FIRE, aim, end, north) == "north"
    upright = (Cell(6, 0), Cell(6, 10))
    east = side_of(WALL_OF_FIRE, *upright, Cell(8, 5), SETTINGS)
    assert side_name(WALL_OF_FIRE, *upright, east) == "east"


def test_a_rings_sides_are_inside_and_outside():
    assert side_of(RING, Cell(10, 8), None, Cell(10, 8), SETTINGS) == 1
    assert side_of(RING, Cell(10, 8), None, Cell(14, 8), SETTINGS) == -1
    assert side_name(RING, Cell(10, 8), None, 1) == "inside"
    assert side_name(RING, Cell(10, 8), None, -1) == "outside"


def test_the_damaging_side_reaches_10_feet_from_the_wall():
    aim, end = Cell(2, 5), Cell(8, 5)
    south = side_of(WALL_OF_FIRE, aim, end, Cell(4, 7), SETTINGS)
    near = side_cells(WALL_OF_FIRE, aim, end, south, 10, SETTINGS)
    assert {Cell(4, 6), Cell(4, 7)} <= near
    assert Cell(4, 8) not in near, "15 ft. off"
    assert not {Cell(4, 4), Cell(4, 5)} & near, "the other side, and the wall"


def test_wall_of_fire_keeps_its_side_and_who_ends_a_turn_by_it():
    aim, end = Cell(2, 5), Cell(8, 5)
    south = side_of(WALL_OF_FIRE, aim, end, Cell(4, 7), SETTINGS)
    record = area_record(
        WALL_OF_FIRE,
        None,
        aim,
        SETTINGS,
        pick="Wall of Fire",
        about=_text("Wall of Fire"),
        end=end,
        side=south,
    )
    assert record["end"] == [8, 5] and record["side"] == south
    assert [4, 7] in record["side_cells"] and "terrain" not in record
    caster = _caster_with(record, name="Wall of Fire")
    by_it, in_it, far = (
        _creature("Goblin", (4, 6)),
        _creature("Orc", (4, 5)),
        _creature("Kobold", (4, 3)),
    )
    chars = [caster, by_it, in_it, far]
    areas = lasting_areas(chars, SETTINGS)
    assert [a.name for a in areas_beside(by_it, areas, SETTINGS)] == ["Wall of Fire"]
    assert areas_beside(in_it, areas, SETTINGS) == [], "in it, not beside it"
    assert areas_beside(far, areas, SETTINGS) == []
    prompt = AreaPrompt(caster, by_it, "Wall of Fire", areas[0].key, ENDS, beside=True)
    assert prompt.prompt == (
        "Clover's Wall of Fire on Goblin (ended its turn by its damaging side)"
    )


def test_a_walls_cover_origin_is_itself():
    record = area_record(WALL_OF_FIRE, None, Cell(2, 5), SETTINGS, end=Cell(4, 5))
    assert record_origin(record) == [Cell(2, 5), Cell(3, 5), Cell(4, 5)]


# ---------------------------------------------------------------------------
# What a wall is as terrain


def test_what_each_wall_is_as_terrain():
    force = wall_terrain("Wall of Force", _text("Wall of Force"))
    assert force == MapObject("Wall of Force", blocks=True, cover=TOTAL)
    blades = wall_terrain("Blade Barrier", _text("Blade Barrier"))
    assert blades == MapObject("Blade Barrier", difficult=True, cover=THREE_QUARTERS)
    assert wall_terrain("Wall of Fire", _text("Wall of Fire")) is None
    assert wall_terrain("Wall of Thorns", _text("Wall of Thorns")) is None


def _force_down_column_6(settings: ArenaSettings = SETTINGS) -> dict:
    force = AreaOfEffect(AreaShape.WALL, 100, 1)
    record = area_record(
        force,
        None,
        Cell(6, 0),
        settings,
        pick="Wall of Force",
        about=_text("Wall of Force"),
        end=Cell(6, 15),
    )
    return _caster_with(record)


def test_wall_of_force_blocks_and_is_total_cover_without_changing_the_map():
    caster = _force_down_column_6()
    left, right = _creature("Goblin", (4, 5)), _creature("Orc", (8, 5))
    chars = [caster, left, right]
    settings = with_kept_walls(SETTINGS, chars)
    assert settings is not SETTINGS and not SETTINGS.terrain, "a copy"
    assert settings.terrain.blocks(Cell(6, 5))
    assert cover_from(left, right, chars, settings).total
    assert not cover_from(left, right, chars, SETTINGS)
    assert all(cell.col < 6 for cell in reachable(left, chars, settings, 30))
    fireball = AreaOfEffect(AreaShape.SPHERE, 20)
    assert Cell(7, 5) not in area_cells(fireball, None, Cell(5, 5), settings)


def test_no_wall_leaves_the_map_as_it_is():
    plain = _creature("Goblin", (4, 5))
    assert with_kept_walls(SETTINGS, [plain]) is SETTINGS
    fire = area_record(
        WALL_OF_FIRE, None, Cell(2, 5), SETTINGS, about=_text("Wall of Fire")
    )
    assert (
        with_kept_walls(SETTINGS, [_caster_with(fire, name="Wall of Fire")]) is SETTINGS
    )


def test_what_is_painted_under_a_wall_stays_painted():
    settings = ArenaSettings()
    settings.terrain.put(Cell(6, 3), Spot(ground=WALL))
    settings.terrain.put(Cell(6, 4), Spot(height_ft=10))
    barrel = MapObject("Barrel", blocks=True, cover=HALF)
    settings.terrain.put(Cell(6, 7), Spot(thing=barrel))
    blades = AreaOfEffect(AreaShape.WALL, 100, 5)
    record = area_record(
        blades,
        None,
        Cell(6, 0),
        settings,
        pick="Blade Barrier",
        about=_text("Blade Barrier"),
        end=Cell(6, 15),
    )
    ruled = with_kept_walls(settings, [_caster_with(record, name="Blade Barrier")])
    assert ruled.terrain.at(Cell(6, 3)).ground == WALL
    assert ruled.terrain.at(Cell(6, 4)).height_ft == 10
    thing = ruled.terrain.at(Cell(6, 4)).thing
    assert thing is not None and thing.name == "Blade Barrier"
    assert ruled.terrain.difficult(Cell(6, 5)) and not ruled.terrain.blocks(Cell(6, 5))
    assert ruled.terrain.at(Cell(6, 7)).thing == barrel, "a barrel still blocks"
    assert settings.terrain.at(Cell(6, 5)).thing is None, "the painted map unchanged"
