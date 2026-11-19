"""A creature's speeds on the battle map, with no Qt (Combat/Arena/speeds.py;
Notes/combat-arena-plan.md, step 26), on plain combatant dicts: which
speeds it has, the one it moves by and switching between them (Rules
Glossary, Speed), what each costs over the ground, water swum (Swimming),
altitude in distances, and falling (Flying, Falling)."""

from dataclasses import dataclass
from typing import Any

from Combat.Arena.arena import (
    MOVED_KEY,
    ArenaSettings,
    distance_ft,
    move_cost,
    movement_ft,
    reachable,
    remaining_ft,
)
from Combat.Arena.geometry import Cell
from Combat.Arena.speeds import (
    ALTITUDE_KEY,
    BURROW,
    CLIMB,
    FLY,
    MODE_KEY,
    SWIM,
    WALK,
    altitude_ft,
    fall_reason,
    falling_dice,
    hovers,
    mode_of,
    speeds,
    speeds_text,
    stored_speeds,
)
from Combat.Arena.terrain import DIFFICULT, WATER, Spot
from Model.Content.CombatModifiers import Movement


def _creature(name: str, at=(0, 0), **keys: Any) -> dict:
    char = {"name": name, "size": "Medium", "hp": 10, "conditions": [], **keys}
    char["position"] = list(at)
    return char


@dataclass
class _Wings:
    """A feature giving a Movement (a species' flight)."""

    given: Movement
    name: str = "Wings"

    def movement(self, sheet):
        return self.given


def _settings(painted: dict[tuple[int, int], Spot] | None = None) -> ArenaSettings:
    settings = ArenaSettings()
    for (col, row), spot in (painted or {}).items():
        settings.terrain.put(Cell(col, row), spot)
    return settings


# ---------------------------------------------------------------------------
# Which speeds


def test_a_stat_blocks_speeds_from_its_fields():
    dragon = _creature(
        "Black Dragon Wyrmling",
        speed_ground_ft=30,
        speed_fly_ft=60,
        speed_swim_ft=30,
    )
    assert speeds(dragon) == {WALK: 30, FLY: 60, SWIM: 30}
    bulette = _creature(
        "Bulette", speed_ground_ft=40, speed_burrow_ft=20, speed_swim_ft=30
    )
    assert speeds(bulette) == {WALK: 40, SWIM: 30, BURROW: 20}
    spider = _creature("Spider", speed_ground_ft=30, speed_climb_ft=30)
    assert speeds(spider) == {WALK: 30, CLIMB: 30}


def test_hovering_is_read_from_the_stat_block_or_a_movement():
    sword = _creature("Flying Sword", speed_ground_ft=5, speed_fly_ft=50)
    sword["hover"] = True
    assert hovers(sword)
    assert not hovers(_creature("Eagle", speed_ground_ft=10, speed_fly_ft=80))
    fly = _creature("Clover", speed=30)
    fly["_feature_objects"] = [_Wings(Movement(fly_ft=60, hovers=True))]
    assert speeds(fly) == {WALK: 30, FLY: 60} and hovers(fly)
    assert speeds_text(fly) == "Walk 30 ft., Fly 60 ft. (hover)"


def test_a_speed_equal_to_its_speed():
    winged = _creature("Aarakocra", speed=30)
    winged["_feature_objects"] = [_Wings(Movement(flies=True, swims=True))]
    assert stored_speeds(winged) == {WALK: 30, FLY: 30, SWIM: 30}


def test_every_speed_changes_as_its_speed_does():
    """Rules Glossary, Speed: "if your Speed is reduced to 0 and you have a
    Climb Speed, your Climb Speed is also reduced to 0"."""
    eagle = _creature("Eagle", speed_ground_ft=10, speed_fly_ft=80)
    eagle["conditions"] = ["Grappled"]
    assert speeds(eagle) == {WALK: 0, FLY: 0}


# ---------------------------------------------------------------------------
# The speed it moves by


def test_it_moves_by_its_speed_until_set_to_another():
    dragon = _creature("Dragon", speed_ground_ft=30, speed_fly_ft=60)
    assert mode_of(dragon) == WALK and movement_ft(dragon) == 30
    dragon[MODE_KEY] = FLY
    assert mode_of(dragon) == FLY and movement_ft(dragon) == 60
    dragon[MODE_KEY] = SWIM  # one it doesn't have
    assert mode_of(dragon) == WALK
    flier = _creature("Stirge", speed_fly_ft=40)
    assert mode_of(flier) == FLY, "a creature that only flies"


def test_switching_counts_what_it_moved_against_the_new_speed():
    """The glossary's example: "if you have a Speed of 30 and a Fly Speed of
    40, you could fly 10 feet, walk 10 feet, and leap into the air to fly
    20 feet more"."""
    you = _creature("You", speed=30, speed_fly_ft=40)
    you[MODE_KEY], you[MOVED_KEY] = FLY, 10
    assert remaining_ft(you) == 30
    you.pop(MODE_KEY)
    you[MOVED_KEY] = 20  # walked 10
    assert remaining_ft(you) == 10
    you[MODE_KEY] = FLY
    assert remaining_ft(you) == 20


def test_a_dash_adds_its_speed_whatever_it_moves_by():
    """Dash: "The increase equals your Speed after applying any
    modifiers"."""
    dragon = _creature("Dragon", speed_ground_ft=30, speed_fly_ft=60, dashes=1)
    dragon[MODE_KEY] = FLY
    assert movement_ft(dragon) == 90


# ---------------------------------------------------------------------------
# What moving by each costs


def test_flying_over_difficult_terrain_water_and_a_ledge_costs_nothing_extra():
    settings = _settings(
        {
            (1, 0): Spot(ground=DIFFICULT),
            (2, 0): Spot(ground=WATER),
            (3, 0): Spot(height_ft=10),
        }
    )
    bird = _creature("Eagle", speed_ground_ft=10, speed_fly_ft=80)
    # Walking: Difficult Terrain 10, water swum 10, and the ledge 5 across
    # and 10 up, each foot of the climb costing 1 extra.
    assert move_cost(bird, [bird], settings, Cell(3, 0)) == 10 + 10 + 5 + 20
    bird[MODE_KEY] = FLY
    assert move_cost(bird, [bird], settings, Cell(3, 0)) == 15


def test_flying_over_an_enemy_is_still_difficult_terrain():
    # A Tiny bird passes a Medium enemy (two sizes larger), which is
    # Difficult Terrain to it in the air as on the ground.
    bird = _creature("Owl", speed_ground_ft=5, speed_fly_ft=60, _is_player=True)
    bird["size"] = "Tiny"
    bird[MODE_KEY] = FLY
    goblin = _creature("Goblin", at=(1, 0))
    assert move_cost(bird, [bird, goblin], _settings(), Cell(2, 0)) == 15


def test_water_is_swum():
    """Swimming: "each foot of movement costs 1 extra foot (2 extra feet in
    Difficult Terrain). You ignore this extra cost if you have a Swim Speed
    and use it to swim"."""
    settings = _settings({(c, 0): Spot(ground=WATER) for c in range(1, 4)})
    assert not settings.terrain.difficult(Cell(1, 0)) and settings.terrain.water(
        Cell(1, 0)
    )
    walker = _creature("Clover", speed=30, _is_player=True)
    assert move_cost(walker, [walker], settings, Cell(2, 0)) == 20
    goblin = _creature("Goblin", at=(1, 0))
    assert move_cost(walker, [walker, goblin], settings, Cell(2, 0)) == 15 + 10
    dragon = _creature("Dragon", speed_ground_ft=30, speed_swim_ft=30)
    dragon[MODE_KEY] = SWIM
    assert move_cost(dragon, [dragon], settings, Cell(3, 0)) == 15


def test_swimming_stays_in_the_water():
    settings = _settings({(c, 0): Spot(ground=WATER) for c in range(1, 3)})
    dragon = _creature("Dragon", speed_ground_ft=30, speed_swim_ft=30)
    dragon[MODE_KEY] = SWIM
    reach = reachable(dragon, [dragon], settings, 30)
    assert set(reach) == {Cell(0, 0), Cell(1, 0), Cell(2, 0)}


def test_burrowing_goes_under_creatures_and_difficult_terrain():
    settings = _settings({(1, 0): Spot(ground=DIFFICULT)})
    bulette = _creature("Bulette", speed_ground_ft=40, speed_burrow_ft=20)
    bulette[MODE_KEY] = BURROW
    knight = _creature("Knight", at=(2, 0), _is_player=True, size="Medium")
    assert move_cost(bulette, [bulette, knight], settings, Cell(3, 0)) == 15
    assert Cell(2, 0) not in reachable(bulette, [bulette, knight], settings, 40)


# ---------------------------------------------------------------------------
# Altitude and falling


def test_altitude_counts_into_distances():
    bird = _creature("Eagle", speed_ground_ft=10, speed_fly_ft=80)
    bird[MODE_KEY], bird[ALTITUDE_KEY] = FLY, 30
    goblin = _creature("Goblin", at=(1, 0))
    assert altitude_ft(bird) == 30
    assert distance_ft(bird, goblin, _settings()) == 35
    bird.pop(MODE_KEY)  # not flying: no altitude
    assert altitude_ft(bird) == 0


def test_a_flyer_falls_when_prone_incapacitated_or_its_fly_speed_is_0():
    bird = _creature("Eagle", speed_ground_ft=10, speed_fly_ft=80)
    bird[MODE_KEY], bird[ALTITUDE_KEY] = FLY, 30
    assert fall_reason(bird) is None
    bird["conditions"] = ["Prone"]
    assert fall_reason(bird) == "Prone"
    bird["conditions"] = ["Stunned"]  # Incapacitated with it
    assert fall_reason(bird) == "Incapacitated"
    bird["conditions"] = ["Grappled"]
    assert fall_reason(bird) == "its Fly Speed is 0"
    bird["hover"] = True
    assert fall_reason(bird) is None, "it hovers"


def test_a_flyer_whose_fly_speed_is_gone_falls():
    """Fly: "When the spell ends, the target falls if it is still aloft"."""
    clover = _creature("Clover", speed=30)
    clover[MODE_KEY], clover[ALTITUDE_KEY] = FLY, 20
    assert fall_reason(clover) == "it can't fly any more"
    clover["_feature_objects"] = [_Wings(Movement(fly_ft=60, hovers=True))]
    assert fall_reason(clover) is None


def test_falling_deals_1d6_for_every_10_feet_to_20d6():
    assert falling_dice(5) == ""
    assert falling_dice(10) == "1d6"
    assert falling_dice(35) == "3d6"
    assert falling_dice(500) == "20d6"
