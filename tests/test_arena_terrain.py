"""The painted battle map, with no Qt (Notes/map-painter-plan.md): terrain
kept as plain JSON, walls and blocking objects nobody enters, Difficult
Terrain that isn't cumulative, climbing between heights (Rules Glossary,
Climbing and Difficult Terrain), height in distances, the map file and
where combatants start. Expected costs are worked out from the glossary's
text, on 5-foot cells counted Manhattan."""

from typing import Any

from Combat.Arena.arena import (
    ArenaSettings,
    distance_ft,
    distance_to_cell_ft,
    fits_at,
    footprint,
    move_cost,
    place_new,
    reachable,
)
from Combat.Arena.geometry import SQUARE_GRID, Cell, rule_named
from Combat.Arena.maps import (
    MapDesign,
    map_path,
    place_at_starts,
    read_map,
    write_map,
)
from Combat.Arena.terrain import (
    DARK,
    DIFFICULT,
    DIM,
    HALF,
    OBJECT_PRESETS,
    WALL,
    WATER,
    MapObject,
    Spot,
    Terrain,
)
from Combat.LogFiles import write_json


def _monster(name: str, at=None, size: str = "Medium", **keys: Any) -> dict:
    char = {"name": name, "size": size, "hp": 7, "speed_ground_ft": 30, **keys}
    if at is not None:
        char["position"] = list(at)
    return char


def _player(name: str, at=None, **keys: Any) -> dict:
    char = {"name": name, "_is_player": True, "size": "Medium", "hp": 20, "speed": 30}
    char.update(keys)
    if at is not None:
        char["position"] = list(at)
    return char


def _settings(**cells: Spot) -> ArenaSettings:
    """A default map with the cells named "C_R" (column_row) painted."""
    settings = ArenaSettings()
    for key, spot in cells.items():
        col, row = key.split("_")[1:]
        settings.terrain.put(Cell(int(col), int(row)), spot)
    return settings


# ---------------------------------------------------------------------------
# Kept as plain JSON


def test_only_painted_cells_are_kept_and_they_round_trip():
    terrain = Terrain()
    terrain.put(Cell(2, 3), Spot(ground=WALL))
    terrain.put(Cell(4, 1), Spot(height_ft=10, light=DIM))
    terrain.put(Cell(5, 5), Spot(thing=MapObject("Barrel", blocks=True, cover=HALF)))
    terrain.put(Cell(6, 6), Spot())  # plain: not kept
    assert set(terrain.cells) == {Cell(2, 3), Cell(4, 1), Cell(5, 5)}
    data = terrain.to_dict()
    assert data["cells"][0] == {
        "at": [4, 1],
        "height": 10,
        "light": "dim",
    }, "row by row"
    assert Terrain.from_dict(data) == terrain


def test_painting_a_cell_back_to_plain_forgets_it():
    terrain = Terrain()
    assert terrain.change(Cell(1, 1), ground=WATER)
    assert not terrain.change(Cell(1, 1), ground=WATER), "nothing changed"
    assert terrain.change(Cell(1, 1), ground="open")
    assert not terrain


def test_a_map_file_with_nonsense_in_it_still_opens():
    terrain = Terrain.from_dict(
        {
            "cells": [
                {"at": [1, 1], "ground": "lava", "light": "neon", "height": "high"},
                {"at": [2, 2], "object": {"cover": "most"}},
                {"no": "at"},
            ]
        }
    )
    assert terrain.at(Cell(1, 1)) == Spot(), "unknown values are plain ground"
    assert terrain.at(Cell(2, 2)).thing == MapObject("Object")


def test_settings_keep_terrain_only_when_painted():
    plain = ArenaSettings()
    assert "terrain" not in plain.to_dict()
    painted = _settings(c_3_3=Spot(ground=WALL))
    assert ArenaSettings.from_dict(painted.to_dict()) == painted
    copy = painted.copy()
    copy.terrain.put(Cell(0, 0), Spot(ground=WATER))
    assert Cell(0, 0) not in painted.terrain.cells, "a copy paints on its own"


def test_what_the_hover_says_of_a_cell():
    terrain = Terrain()
    terrain.put(
        Cell(1, 1),
        Spot(
            ground=DIFFICULT,
            height_ft=-5,
            light=DARK,
            thing=MapObject("Table", difficult=True, cover=HALF),
        ),
    )
    assert terrain.describe(Cell(1, 1)) == [
        "Difficult Terrain",
        "5 ft. down",
        "Darkness (Heavily Obscured)",
        "Table (Difficult Terrain, Half Cover)",
    ]
    assert terrain.describe(Cell(9, 9)) == []


def test_every_preset_is_something_the_map_counts():
    for preset in OBJECT_PRESETS:
        assert preset.blocks or preset.difficult or preset.hazard, preset.name


# ---------------------------------------------------------------------------
# Walls, blocking objects and Difficult Terrain


def test_nobody_stands_on_a_wall_or_a_barrel():
    settings = _settings(
        c_5_5=Spot(ground=WALL), c_6_5=Spot(thing=MapObject("Barrel", blocks=True))
    )
    goblin = _monster("Goblin", (4, 5))
    assert not fits_at(goblin, Cell(5, 5), [goblin], settings)
    assert not fits_at(goblin, Cell(6, 5), [goblin], settings)
    assert fits_at(goblin, Cell(7, 5), [goblin], settings)
    ogre = _monster("Ogre", (0, 0), size="Large")
    assert not fits_at(ogre, Cell(4, 4), [ogre], settings), "one of its 4 cells"


def test_a_wall_is_walked_around():
    # A wall from row 0 to row 4 in column 5, a goblin at its foot's left.
    settings = ArenaSettings()
    for row in range(5):
        settings.terrain.put(Cell(5, row), Spot(ground=WALL))
    goblin = _monster("Goblin", (4, 0))
    reach = reachable(goblin, [goblin], settings, 30)
    assert not any(cell.col == 5 and cell.row < 5 for cell in reach)
    # Straight across is 2 cells; around the wall's end (row 5) is 12.
    assert move_cost(goblin, [goblin], settings, Cell(6, 0)) == 60


def test_difficult_terrain_costs_double():
    settings = ArenaSettings()
    for col in (1, 2):
        settings.terrain.put(Cell(col, 0), Spot(ground=DIFFICULT))
    goblin = _monster("Goblin", (0, 0))
    assert move_cost(goblin, [goblin], settings, Cell(2, 0)) == 20
    assert move_cost(goblin, [goblin], settings, Cell(3, 0)) == 25, "out costs 5"
    settings.terrain.put(Cell(1, 0), Spot(ground=WATER))
    assert move_cost(goblin, [goblin], settings, Cell(1, 0)) == 10, "water too"
    table = MapObject("Table", difficult=True)
    settings.terrain.put(Cell(1, 0), Spot(thing=table))
    assert move_cost(goblin, [goblin], settings, Cell(1, 0)) == 10, "furniture too"


def test_difficult_terrain_isnt_cumulative():
    """Rules Glossary, Difficult Terrain: "either a space is Difficult
    Terrain or it isn't" - an enemy's space on rubble costs 10 ft. a cell,
    not 15."""
    settings = _settings(c_1_0=Spot(ground=DIFFICULT))
    clover = _player("Clover", (0, 0))
    fallen = _monster("Goblin", (1, 0), hp=0)  # at 0 HP: passed through
    assert move_cost(clover, [clover, fallen], settings, Cell(2, 0)) == 15


def test_crawling_through_difficult_terrain_adds_up():
    """Crawling and Difficult Terrain each cost 1 extra foot: 3 ft. a foot."""
    settings = _settings(c_1_0=Spot(ground=DIFFICULT))
    prone = _monster("Goblin", (0, 0), conditions=["Prone"])
    assert move_cost(prone, [prone], settings, Cell(1, 0)) == 15


# ---------------------------------------------------------------------------
# Heights


def test_a_step_up_a_ledge_is_a_climb():
    """Rules Glossary, Climbing: each foot costs 1 extra foot, 2 extra in
    Difficult Terrain, none with a Climb Speed. A 5-ft. step onto a 10-ft.
    ledge: 5 + 10 x 2."""
    settings = _settings(c_1_0=Spot(height_ft=10))
    goblin = _monster("Goblin", (0, 0))
    assert move_cost(goblin, [goblin], settings, Cell(1, 0)) == 25
    assert move_cost(goblin, [goblin], settings, Cell(2, 0)) == 20, "walked around"
    ledge = ArenaSettings()
    for row in range(ledge.height):
        ledge.terrain.put(Cell(1, row), Spot(height_ft=10))
    assert move_cost(goblin, [goblin], ledge, Cell(2, 0)) == 50, "up and down again"
    spider = _monster("Spider", (0, 0), speed_climb_ft=30)
    assert move_cost(spider, [spider], settings, Cell(1, 0)) == 15
    settings.terrain.put(Cell(1, 0), Spot(ground=DIFFICULT, height_ft=10))
    assert move_cost(goblin, [goblin], settings, Cell(1, 0)) == 10 + 30


def test_walking_along_high_ground_costs_nothing_extra():
    settings = ArenaSettings()
    for col in range(4):
        settings.terrain.put(Cell(col, 0), Spot(height_ft=20))
    goblin = _monster("Goblin", (0, 0))
    assert move_cost(goblin, [goblin], settings, Cell(3, 0)) == 15


def test_height_counts_into_distances():
    settings = _settings(c_1_0=Spot(height_ft=10))
    archer = _monster("Archer", (1, 0))
    knight = _player("Knight", (0, 0))
    assert distance_ft(archer, knight, settings) == 15
    assert distance_to_cell_ft(knight, Cell(1, 0), settings) == 15
    assert distance_to_cell_ft(archer, Cell(1, 0), settings) == 0
    pit = _settings(c_3_0=Spot(height_ft=-20))
    assert distance_to_cell_ft(knight, Cell(3, 0), pit) == 35


def test_a_large_creature_stands_on_its_highest_cell():
    settings = _settings(c_1_1=Spot(height_ft=10))
    ogre = _monster("Ogre", (0, 0), size="Large")
    goblin = _monster("Goblin", (2, 0))
    assert distance_ft(ogre, goblin, settings) == 5 + 10


def test_with_height_adds_for_manhattan():
    assert rule_named("manhattan").with_height(25, 10) == 35


# ---------------------------------------------------------------------------
# Where tokens start


def test_new_tokens_never_start_on_a_wall():
    settings = ArenaSettings()
    for row in range(settings.height):
        settings.terrain.put(Cell(0, row), Spot(ground=WALL))
    party = [_player("Clover"), _player("Edmund")]
    place_new(party, settings)
    assert all(footprint(c, settings.distance_rule)[0].col == 1 for c in party)


def test_combatants_start_where_the_map_says():
    settings = _settings(c_10_5=Spot(ground=WALL))
    goblin, boss = _monster("Goblin 1"), _monster("Goblin Boss")
    clover = _player("Clover", (3, 3))
    starts = {"Goblin 1": Cell(12, 5), "Goblin Boss": Cell(10, 5), "Clover": Cell(1, 1)}
    placed = place_at_starts([goblin, boss, clover], starts, settings)
    assert goblin["position"] == [12, 5]
    assert boss["position"] in ([9, 5], [11, 5], [10, 4], [10, 6]), "beside the wall"
    assert clover["position"] == [3, 3], "already on the map"
    assert placed == [goblin, boss]


def test_a_start_someone_already_holds_goes_to_the_nearest_free_cell():
    settings = ArenaSettings()
    first, second = _monster("Goblin 1"), _monster("Goblin 2")
    place_at_starts(
        [first, second], {"Goblin 1": Cell(5, 5), "Goblin 2": Cell(5, 5)}, settings
    )
    assert first["position"] == [5, 5]
    assert second["position"] != [5, 5]
    assert distance_ft(first, second, settings) == 5


# ---------------------------------------------------------------------------
# The map file


def test_the_map_file_sits_beside_the_combat_logs(tmp_path):
    logs = tmp_path / "Campaign" / "CombatLogs"
    assert map_path(logs, "goblins") == tmp_path / "Campaign" / "Maps" / "goblins.json"


def test_a_map_is_saved_and_read_back(tmp_path):
    path = tmp_path / "Maps" / "goblins.json"
    assert read_map(path) is None
    design = MapDesign(ArenaSettings(width=12, height=10), {"Goblin": Cell(3, 4)})
    design.settings.terrain.put(Cell(1, 1), Spot(ground=WALL))
    write_map(path, design)
    assert read_map(path) == design
    write_json(path, {})
    assert read_map(path) is None, "an empty file is no map"


def test_a_smaller_map_drops_what_is_past_its_edge():
    design = MapDesign(ArenaSettings(width=10, height=10))
    design.settings.terrain.put(Cell(9, 9), Spot(ground=WALL))
    design.settings.terrain.put(Cell(2, 2), Spot(ground=WALL))
    design.starts = {"Near": Cell(1, 1), "Far": Cell(8, 8)}
    design.settings.width = design.settings.height = 5
    cropped = design.cropped()
    assert set(cropped.settings.terrain.cells) == {Cell(2, 2)}
    assert cropped.starts == {"Near": Cell(1, 1)}
    assert Cell(9, 9) in design.settings.terrain.cells, "the design is kept"


# ---------------------------------------------------------------------------
# Geometry the painter uses


def test_a_block_between_two_cells():
    block = SQUARE_GRID.between(Cell(3, 1), Cell(1, 2))
    assert block == [
        Cell(1, 1),
        Cell(2, 1),
        Cell(3, 1),
        Cell(1, 2),
        Cell(2, 2),
        Cell(3, 2),
    ]


def test_a_cells_edges_name_the_cell_beyond_them():
    edges = SQUARE_GRID.edges(Cell(1, 1), 10)
    assert [other for other, _ in edges] == SQUARE_GRID.neighbours(Cell(1, 1))
    assert dict(edges)[Cell(1, 0)] == ((10, 10), (20, 10)), "the top edge"
