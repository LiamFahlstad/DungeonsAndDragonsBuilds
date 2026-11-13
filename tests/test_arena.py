"""The battle map's state (Combat/Arena/arena.py), on plain combatant dicts:
footprints, distances between creatures, the reach of a move and where new
tokens go."""

from typing import Any

from Combat.Arena.arena import (
    ArenaSettings,
    distance_ft,
    footprint,
    occupied,
    place_beside,
    place_new,
    place_summons,
    reachable,
    walking_speed_ft,
)
from Combat.Arena.geometry import Cell
from Combat.Effects.active_effects import give_modifiers
from Model.Content.CombatModifiers import Size, Speed

SETTINGS = ArenaSettings()
RULE = SETTINGS.distance_rule


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


def _diamond(center: Cell, steps: int, settings: ArenaSettings = SETTINGS) -> set:
    return {
        Cell(c, r)
        for c in range(settings.width)
        for r in range(settings.height)
        if abs(c - center.col) + abs(r - center.row) <= steps
    }


# ---------------------------------------------------------------------------
# Settings


def test_settings_default_for_a_log_without_any():
    assert ArenaSettings.from_dict({}) == ArenaSettings()
    assert ArenaSettings.from_dict(None) == ArenaSettings(24, 16, 5, "manhattan")


def test_settings_round_trip():
    settings = ArenaSettings(width=10, height=8, cell_ft=10)
    assert ArenaSettings.from_dict(settings.to_dict()) == settings


# ---------------------------------------------------------------------------
# Footprints and distances


def test_footprints_by_size():
    assert footprint(_monster("Goblin", (5, 5), "Small"), RULE) == [Cell(5, 5)]
    assert len(footprint(_monster("Ogre", (5, 5), "Large"), RULE)) == 4
    assert len(footprint(_monster("Giant", (5, 5), "Huge"), RULE)) == 9
    assert len(footprint(_monster("Worm", (5, 5), "Gargantuan"), RULE)) == 16
    assert footprint(_monster("Ghost"), RULE) == [], "not on the map"


def test_an_enlarged_medium_creature_takes_2_by_2():
    """The footprint reads size_in_use."""
    fighter = _player("Fighter", (2, 2), conditions=["Enlarge/Reduce"])
    give_modifiers(fighter, "Enlarge/Reduce", (Size(steps=1),))
    assert set(footprint(fighter, RULE)) == {
        Cell(2, 2),
        Cell(3, 2),
        Cell(2, 3),
        Cell(3, 3),
    }


def test_a_large_creature_counts_from_its_nearest_cell():
    ogre = _monster("Ogre", (5, 5), "Large")  # covers (5..6, 5..6)
    beside = _player("Fighter", (7, 6))
    assert distance_ft(ogre, beside, SETTINGS) == 5
    far = _player("Rogue", (10, 5))
    assert distance_ft(ogre, far, SETTINGS) == 20
    assert distance_ft(far, ogre, SETTINGS) == 20


def test_no_distance_off_the_map():
    assert distance_ft(_monster("Goblin", (1, 1)), _player("Fighter"), SETTINGS) is None


def test_occupied_cells_name_their_creature():
    ogre = _monster("Ogre", (0, 0), "Large")
    taken = occupied([ogre, _monster("Ghost")], RULE)
    assert len(taken) == 4 and all(c is ogre for c in taken.values())


# ---------------------------------------------------------------------------
# Speed


def test_the_walking_speed_in_use():
    assert walking_speed_ft(_monster("Goblin")) == 30
    assert walking_speed_ft(_player("Fighter", speed=25)) == 25
    hasted = _player("Fighter", conditions=["Haste"])
    give_modifiers(hasted, "Haste", (Speed(multiplier=2),))
    assert walking_speed_ft(hasted) == 60
    flyer = {"name": "Bat", "speed_fly_ft": 30, "speed_climb_ft": 10}
    assert walking_speed_ft(flyer) == 30, "its highest speed when it can't walk"
    assert walking_speed_ft({"name": "Statue"}) is None


def test_grappled_has_speed_0():
    """DI-084: the conditions' Speed 0 counts."""
    for condition in (
        "Grappled",
        "Restrained",
        "Paralyzed",
        "Petrified",
        "Unconscious",
    ):
        assert walking_speed_ft(_monster("Goblin", conditions=[condition])) == 0


# ---------------------------------------------------------------------------
# Reach


def test_30_feet_reach_the_manhattan_diamond_of_6_steps():
    goblin = _monster("Goblin", (10, 8))
    reach = reachable(goblin, [goblin], SETTINGS, 30)
    assert set(reach) == _diamond(Cell(10, 8), 6)
    assert reach[Cell(10, 8)] == 0
    assert reach[Cell(13, 5)] == 30
    assert reach[Cell(11, 8)] == 5


def test_the_map_edge_cuts_the_reach():
    goblin = _monster("Goblin", (0, 0))
    reach = reachable(goblin, [goblin], SETTINGS, 10)
    assert set(reach) == {
        Cell(0, 0),
        Cell(1, 0),
        Cell(0, 1),
        Cell(2, 0),
        Cell(1, 1),
        Cell(0, 2),
    }


def test_an_enemy_in_a_corridor_blocks_the_way():
    """A one-cell-wide map: the enemy's space can't be crossed or ended on."""
    corridor = ArenaSettings(width=10, height=1)
    fighter = _player("Fighter", (0, 0))
    goblin = _monster("Goblin", (2, 0))
    reach = reachable(fighter, [fighter, goblin], corridor, 30)
    assert set(reach) == {Cell(0, 0), Cell(1, 0)}


def test_an_ally_is_passed_through_but_never_ended_on():
    corridor = ArenaSettings(width=10, height=1)
    fighter = _player("Fighter", (0, 0))
    cleric = _player("Cleric", (2, 0))
    reach = reachable(fighter, [fighter, cleric], corridor, 30)
    assert Cell(2, 0) not in reach
    assert reach[Cell(3, 0)] == 15, "an ally's space isn't Difficult Terrain"
    assert set(reach) == {Cell(c, 0) for c in range(7)} - {Cell(2, 0)}


def test_a_passable_enemy_is_difficult_terrain():
    """A Tiny-or-two-sizes-apart creature can be passed; a creature that
    isn't Tiny or an ally makes its space Difficult Terrain."""
    corridor = ArenaSettings(width=10, height=1)
    halfling = _player("Halfling", (0, 0), size="Small")
    ogre = _monster("Ogre", (2, 0), "Large")
    reach = reachable(halfling, [halfling, ogre], corridor, 30)
    # The Ogre's two cells on this one-row map cost double: 5 + 10 + 10, and
    # the step out of them 5 more.
    assert Cell(2, 0) not in reach and Cell(3, 0) not in reach
    assert reach[Cell(4, 0)] == 30


def test_an_incapacitated_enemy_is_passed_through():
    corridor = ArenaSettings(width=10, height=1)
    fighter = _player("Fighter", (0, 0))
    stunned = _monster("Goblin", (1, 0), conditions=["Stunned"])
    reach = reachable(fighter, [fighter, stunned], corridor, 30)
    assert Cell(1, 0) not in reach
    assert reach[Cell(2, 0)] == 15, "its space is still Difficult Terrain"


def test_a_tiny_enemy_is_passed_at_no_extra_cost():
    corridor = ArenaSettings(width=10, height=1)
    fighter = _player("Fighter", (0, 0))
    rat = _monster("Rat", (1, 0), "Tiny")
    assert reachable(fighter, [fighter, rat], corridor, 30)[Cell(2, 0)] == 10


def test_a_grappled_creature_reaches_nothing():
    goblin = _monster("Goblin", (5, 5), conditions=["Grappled"])
    feet = walking_speed_ft(goblin)
    assert reachable(goblin, [goblin], SETTINGS, feet) == {Cell(5, 5): 0}


def test_a_prone_creature_crawls_half_as_far():
    goblin = _monster("Goblin", (10, 8), conditions=["Prone"])
    reach = reachable(goblin, [goblin], SETTINGS, 30)
    assert set(reach) == _diamond(Cell(10, 8), 3)
    assert reach[Cell(11, 8)] == 10


def test_a_large_creature_needs_room_for_its_whole_footprint():
    corridor = ArenaSettings(width=10, height=2)
    ogre = _monster("Ogre", (0, 0), "Large")
    reach = reachable(ogre, [ogre], corridor, 40)
    assert set(reach) == {Cell(c, 0) for c in range(9)}


def test_off_the_map_reaches_nothing():
    goblin = _monster("Goblin")
    assert reachable(goblin, [goblin], SETTINGS, 30) == {}


# ---------------------------------------------------------------------------
# Placing tokens


def test_place_new_puts_the_sides_apart_without_overlaps():
    party = [_player(f"P{i}") for i in range(4)]
    enemies = [_monster(f"Goblin {i}") for i in range(5)] + [
        _monster("Ogre", size="Large")
    ]
    already = _monster("Scout", (12, 8))
    everyone = party + enemies + [already]
    placed = place_new(everyone, SETTINGS)
    assert len(placed) == 10 and already not in placed
    assert already["position"] == [12, 8], "a placed token isn't moved"
    assert all(p["position"][0] == 0 for p in party)
    assert all(e["position"][0] >= SETTINGS.width - 2 for e in enemies)
    ogre_cells = footprint(enemies[-1], RULE)
    assert max(c.col for c in ogre_cells) == SETTINGS.width - 1, "against the edge"
    cells = [cell for char in everyone for cell in footprint(char, RULE)]
    assert len(cells) == len(set(cells)), "no overlaps"
    assert all(SETTINGS.on_map(c) for c in cells)


def test_a_summon_comes_out_beside_its_owner():
    druid = _player("Druid", (5, 5))
    goblin = _monster("Goblin", (6, 5))
    wolf = _monster("Wolf", summon_of="Druid")
    cell = place_beside(wolf, druid, [druid, goblin, wolf], SETTINGS)
    assert cell is not None and cell != Cell(6, 5)
    wolf["position"] = cell.to_list()
    assert distance_ft(wolf, druid, SETTINGS) == 5


def test_no_place_beside_an_owner_off_the_map():
    assert place_beside(_monster("Wolf"), _player("Druid"), [], SETTINGS) is None


def test_summons_come_out_beside_owners_on_the_map():
    druid = _player("Druid", (5, 5))
    wolf = _monster("Wolf", summon_of="Druid")
    stray = _monster("Hawk", summon_of="Bard")  # owner not in the fight
    place_summons([wolf, stray], [druid], SETTINGS)
    assert distance_ft(wolf, druid, SETTINGS) == 5
    assert "position" not in stray
    off = _player("Cleric")
    spirit = _monster("Spirit", summon_of="Cleric")
    place_summons([spirit], [off], SETTINGS)
    assert "position" not in spirit, "its owner isn't on the map"


def test_a_move_costs_the_cheapest_walk():
    from Combat.Arena.arena import move_cost, remaining_ft, straight_ft

    corridor = ArenaSettings(width=10, height=3)
    fighter = _player("Fighter", (0, 1))
    wall = [_monster(f"Goblin {r}", (2, r)) for r in range(3)]
    everyone = [fighter, *wall]
    assert move_cost(fighter, everyone, corridor, Cell(1, 1)) == 5
    assert move_cost(fighter, everyone, corridor, Cell(4, 1)) is None, "walled off"
    assert straight_ft(fighter, Cell(4, 1), corridor) == 20
    fighter["moved_ft"] = 10
    assert remaining_ft(fighter) == 20
    assert remaining_ft({"name": "Statue"}) == 0
