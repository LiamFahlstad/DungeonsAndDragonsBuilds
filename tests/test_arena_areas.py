"""Areas of effect on the battle map (Notes/combat-arena-plan.md, step 10),
with no Qt: the area a rules text states, the cells each shape covers on
squares with the Manhattan rule, and who stands in them. The shapes are the
Rules Glossary's (Areas of Effect); how they sit on the grid is
Combat/Arena/areas.py's docstring."""

import pytest

from Combat.Arena.areas import (
    AreaOfEffect,
    AreaShape,
    area_cells,
    creatures_in,
    parse_area,
    point_range_ft,
    spell_range_ft,
)
from Combat.Arena.arena import ArenaSettings
from Combat.Arena.geometry import Cell
from Core.Definitions import CreatureSize

SETTINGS = ArenaSettings()  # 24 x 16 cells of 5 ft.
SOURCE = {"name": "Caster", "position": [5, 5]}


def _cells(*pairs: tuple[int, int]) -> set[Cell]:
    return {Cell(c, r) for c, r in pairs}


@pytest.mark.parametrize(
    "text, area",
    [
        (
            "Each creature in a 20-foot-radius Sphere centered on that point",
            AreaOfEffect(AreaShape.SPHERE, 20),
        ),
        ("each creature in a 15-foot Cone", AreaOfEffect(AreaShape.CONE, 15)),
        (
            "Each creature in a 100-foot-long, 5-foot-wide Line",
            AreaOfEffect(AreaShape.LINE, 100, 5),
        ),
        (
            "A Line of strong wind 60 feet long and 10 feet wide blasts from you",
            AreaOfEffect(AreaShape.LINE, 60, 10),
        ),
        (
            "a Line 60 feet long and 10 feet wide",
            AreaOfEffect(AreaShape.LINE, 60, 10),
        ),
        (
            "You unleash a wave of thunderous energy. Each creature in a 15-foot"
            " Cube originating from you makes a Constitution saving throw.",
            AreaOfEffect(AreaShape.CUBE, 15, from_source=True),
        ),
        (
            "Protective spirits flit around you in a 15-foot Emanation",
            AreaOfEffect(AreaShape.EMANATION, 15),
        ),
        (
            "a 10-foot-radius, 40-foot-high Cylinder centered on a point",
            AreaOfEffect(AreaShape.CYLINDER, 10),
        ),
        ("Self (10-foot-radius sphere)", AreaOfEffect(AreaShape.SPHERE, 10, 5, True)),
        (
            "All other creatures within 5 feet of you must succeed on a save",
            AreaOfEffect(AreaShape.EMANATION, 5),
        ),
        (
            "Each creature within 5 feet of that point makes a Dexterity save",
            AreaOfEffect(AreaShape.SPHERE, 5),
        ),
        (
            "grease covers the ground in a 10-foot square",
            AreaOfEffect(AreaShape.CUBE, 10),
        ),
        (
            "a beam of light in a 5-foot-wide, 60-foot-long Line",
            AreaOfEffect(AreaShape.LINE, 60, 5),
        ),
        (
            "Range: Self (15-foot radius). You create a burst of lightning",
            AreaOfEffect(AreaShape.SPHERE, 15, from_source=True),
        ),
    ],
)
def test_the_area_a_text_states(text, area):
    assert parse_area(text) == area


def test_the_first_area_stated_is_the_one():
    text = "a 20-foot Cube appears. Later, a 60-foot Cone of cold."
    assert parse_area(text) == AreaOfEffect(AreaShape.CUBE, 20)


@pytest.mark.parametrize(
    "text",
    [
        "Make a ranged spell attack against a creature within 120 feet.",
        "You teleport up to 30 feet to an unoccupied space you can see.",
        "",
    ],
)
def test_a_text_with_no_area(text):
    assert parse_area(text) is None


def test_centered_on_a_point_is_not_around_the_source():
    area = parse_area("a 20-foot-radius Sphere centered on the point you choose")
    assert area == AreaOfEffect(AreaShape.SPHERE, 20)


def test_a_sphere_is_centred_on_the_cell_aimed_at_and_counted_by_the_rule():
    """Manhattan: 10 ft. is two steps, so a diamond of 13 cells, its centre
    in it (a Sphere's point of origin is included)."""
    cells = area_cells(
        AreaOfEffect(AreaShape.SPHERE, 10), SOURCE, Cell(10, 8), SETTINGS
    )
    assert len(cells) == 13
    assert Cell(10, 8) in cells
    assert {Cell(12, 8), Cell(10, 6), Cell(11, 9)} <= cells
    assert Cell(12, 9) not in cells, "three steps away"


def test_a_sphere_aimed_at_the_source_catches_it():
    cells = area_cells(AreaOfEffect(AreaShape.SPHERE, 5), SOURCE, Cell(5, 5), SETTINGS)
    assert creatures_in([SOURCE], cells, SETTINGS) == [SOURCE]


def test_an_area_stops_at_the_map_edge():
    cells = area_cells(AreaOfEffect(AreaShape.SPHERE, 5), SOURCE, Cell(0, 0), SETTINGS)
    assert cells == _cells((0, 0), (1, 0), (0, 1))


def test_an_emanation_leaves_the_source_out_and_needs_no_aim():
    cells = area_cells(AreaOfEffect(AreaShape.EMANATION, 5), SOURCE, None, SETTINGS)
    assert cells == _cells((5, 4), (6, 5), (5, 6), (4, 5))


def test_a_sphere_around_the_source_is_an_emanation():
    around = AreaOfEffect(AreaShape.SPHERE, 10, from_source=True)
    emanation = AreaOfEffect(AreaShape.EMANATION, 10)
    assert not around.is_aimed
    assert area_cells(around, SOURCE, Cell(0, 0), SETTINGS) == area_cells(
        emanation, SOURCE, None, SETTINGS
    )


def test_a_large_sources_emanation_reaches_from_its_nearest_cell():
    ogre = {"name": "Ogre", "position": [5, 5], "size": CreatureSize.LARGE}
    cells = area_cells(AreaOfEffect(AreaShape.EMANATION, 5), ogre, None, SETTINGS)
    assert cells == _cells(
        (5, 4), (6, 4), (7, 5), (7, 6), (5, 7), (6, 7), (4, 5), (4, 6)
    )


def test_an_aimed_area_not_aimed_yet_covers_nothing():
    for shape in (AreaShape.SPHERE, AreaShape.CONE, AreaShape.LINE, AreaShape.CUBE):
        assert area_cells(AreaOfEffect(shape, 15), SOURCE, None, SETTINGS) == set()


def test_a_source_off_the_map_has_no_cone():
    area = AreaOfEffect(AreaShape.CONE, 15)
    assert area_cells(area, {"name": "Away"}, Cell(8, 5), SETTINGS) == set()


def test_a_cone_widens_as_it_goes_but_reaches_no_further_than_15_ft():
    """15 feet east: as wide at each cell as it is far from the middle of
    the source's space, and no cell further than 3 steps: 1, 3, then the
    one cell 3 steps straight ahead (G5 and G7 are 4 steps: 20 ft.)."""
    cells = area_cells(AreaOfEffect(AreaShape.CONE, 15), SOURCE, Cell(12, 5), SETTINGS)
    assert cells == _cells((6, 5), (7, 4), (7, 5), (7, 6), (8, 5))


def test_a_cone_goes_where_it_is_aimed():
    """The same Cone aimed north: the source's cell is never in it."""
    cells = area_cells(AreaOfEffect(AreaShape.CONE, 15), SOURCE, Cell(5, 0), SETTINGS)
    assert cells == _cells((5, 4), (4, 3), (5, 3), (6, 3), (5, 2))


def test_a_diagonal_cone_keeps_both_sides_of_its_spine():
    """Aimed exactly diagonally, a 15-foot Cone's first step can only be
    straight (a diagonal cell is 10 ft. away), so it takes both, and is
    the same on either side of the diagonal."""
    cells = area_cells(AreaOfEffect(AreaShape.CONE, 15), SOURCE, Cell(10, 10), SETTINGS)
    assert cells == _cells((6, 5), (5, 6), (6, 6), (7, 6), (6, 7))
    small = area_cells(AreaOfEffect(AreaShape.CONE, 5), SOURCE, Cell(10, 10), SETTINGS)
    assert small == _cells((6, 5), (5, 6)), "never empty"


AIMS = [
    Cell(c, r) for c in (0, 5, 9, 12, 20) for r in (0, 3, 5, 8, 15) if (c, r) != (5, 5)
]


@pytest.mark.parametrize("shape", [AreaShape.CONE, AreaShape.LINE])
@pytest.mark.parametrize("size", [5, 15, 30, 60])
def test_nothing_in_a_cone_or_line_is_further_than_its_size(shape, size):
    """By the map's own count, which the hover shows, at every angle."""
    rule = SETTINGS.distance_rule
    for aim in AIMS:
        cells = area_cells(AreaOfEffect(shape, size), SOURCE, aim, SETTINGS)
        assert cells, aim
        assert max(rule.feet(Cell(5, 5), c, 5) for c in cells) <= size, aim


def test_a_cone_aimed_at_its_source_covers_nothing():
    area = AreaOfEffect(AreaShape.CONE, 15)
    assert area_cells(area, SOURCE, Cell(5, 5), SETTINGS) == set()


def test_a_line_is_as_long_as_it_says_from_the_sources_edge():
    cells = area_cells(AreaOfEffect(AreaShape.LINE, 30), SOURCE, Cell(20, 5), SETTINGS)
    assert cells == {Cell(c, 5) for c in range(6, 12)}


@pytest.mark.parametrize("aim", [Cell(20, 5), Cell(15, 15), Cell(8, 15), Cell(0, 2)])
def test_a_5_foot_line_is_one_unbroken_row_at_any_angle(aim):
    """30 feet: six cells, each one step further than the last, so no
    creature slips between two that only touch at a corner."""
    rule = SETTINGS.distance_rule
    cells = area_cells(AreaOfEffect(AreaShape.LINE, 30), SOURCE, aim, SETTINGS)
    steps = sorted(rule.steps(Cell(5, 5), c) for c in cells)
    assert steps == [1, 2, 3, 4, 5, 6]


def test_a_wider_line_covers_as_many_rows_as_it_is_wide():
    """20 by 10 feet east: two rows (the second on one side, as a 10-foot
    width has no middle row), the second row's last cell 25 ft. away and
    so left out."""
    cells = area_cells(
        AreaOfEffect(AreaShape.LINE, 20, 10), SOURCE, Cell(20, 5), SETTINGS
    )
    assert cells == {Cell(c, 5) for c in (6, 7, 8, 9)} | {Cell(c, 4) for c in (6, 7, 8)}
    wide = area_cells(
        AreaOfEffect(AreaShape.LINE, 10, 15), SOURCE, Cell(20, 5), SETTINGS
    )
    assert {c.row for c in wide} == {4, 5, 6}


def test_a_cube_is_centred_on_the_cell_aimed_at():
    cells = area_cells(AreaOfEffect(AreaShape.CUBE, 15), SOURCE, Cell(10, 10), SETTINGS)
    assert cells == {Cell(c, r) for c in (9, 10, 11) for r in (9, 10, 11)}


def test_a_cube_from_the_source_sits_against_the_side_aimed_at():
    """Thunderwave: a 15-foot Cube touching the caster's space, on the side
    of the cell aimed at, the caster outside it."""
    area = AreaOfEffect(AreaShape.CUBE, 15, from_source=True)
    east = area_cells(area, SOURCE, Cell(12, 5), SETTINGS)
    assert east == {Cell(c, r) for c in (6, 7, 8) for r in (4, 5, 6)}
    north = area_cells(area, SOURCE, Cell(5, 0), SETTINGS)
    assert north == {Cell(c, r) for c in (4, 5, 6) for r in (2, 3, 4)}


def test_who_is_in_an_area_counts_any_cell_of_their_space():
    # Its nearest cell, H7, is in the Cone: it's 15 ft. away.
    tiger = {"name": "Tiger", "position": [7, 6], "size": CreatureSize.LARGE}
    goblin = {"name": "Goblin", "position": [12, 12]}
    away = {"name": "Off the map"}
    cells = area_cells(AreaOfEffect(AreaShape.CONE, 15), SOURCE, Cell(12, 5), SETTINGS)
    assert creatures_in([SOURCE, tiger, goblin, away], cells, SETTINGS) == [tiger]


@pytest.mark.parametrize(
    "area, text",
    [
        (AreaOfEffect(AreaShape.SPHERE, 20), "20-foot-radius Sphere"),
        (AreaOfEffect(AreaShape.LINE, 100), "100-foot-long, 5-foot-wide Line"),
        (AreaOfEffect(AreaShape.CUBE, 15, from_source=True), "15-foot Cube from you"),
        (
            AreaOfEffect(AreaShape.SPHERE, 10, from_source=True),
            "10-foot-radius Sphere around you",
        ),
        (AreaOfEffect(AreaShape.EMANATION, 10), "10-foot Emanation"),
    ],
)
def test_an_areas_text(area, text):
    assert area.text == text


@pytest.mark.parametrize(
    "range_text, feet",
    [
        ("150 feet", 150),
        ("1,000 feet", 1000),
        ("1 mile", 5280),
        ("Touch", 5),
        ("Self", None),
        ("Self (15-foot cone)", None),
        ("Sight", None),
    ],
)
def test_a_spells_range_in_feet(range_text, feet):
    assert spell_range_ft(range_text) == feet


@pytest.mark.parametrize(
    "text, feet",
    [
        (
            "each creature in a 20-foot-radius Sphere centered on a point within 120 feet",
            120,
        ),
        ("a 15-foot Cube centered on a point you can see within 60 feet of you", 60),
        ("each creature in a 15-foot Cone", None),
    ],
)
def test_how_far_away_an_areas_point_may_be(text, feet):
    assert point_range_ft(text) == feet
