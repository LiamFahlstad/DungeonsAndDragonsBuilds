"""How what a creature has changes its moves on the battle map
(Combat/Arena/arena.py's movement_rules; Model/Content/CombatModifiers.py's
Movement): Halfling Nimbleness, Incorporeal Movement, a Swarm, Freedom of
Movement, Speedy and Fairy Trickster's Difficult Terrain after a Dash or a
Disengage, a Climb Speed equal to its Speed, and the cost of standing up
from Prone (Rules Glossary, Prone: half its Speed; Athlete's Hop Up: 5 ft.).
Expected costs are worked out from the rules text, on 5-foot cells counted
Manhattan."""

from typing import Any

import pytest

from CharacterContent.Features.CharacterFeats.GeneralFeats import (
    Athlete,
    FairyTrickster,
    Speedy,
)
from CharacterContent.Features.SpeciesFeatures.HalflingFeatures import (
    HalflingNimbleness,
)
from CharacterContent.Spells.SpellClasses.Level2 import SpiderClimb
from CharacterContent.Spells.SpellClasses.Level4 import FreedomOfMovement
from Combat.Arena.arena import (
    ArenaSettings,
    can_end_at,
    move_cost,
    movement_rules,
    reachable,
    stand_up_ft,
)
from Combat.Arena.geometry import Cell
from Combat.Arena.terrain import DIFFICULT, WALL, Spot
from Combat.Effects.active_effects import give_modifiers
from Core.Definitions import Ability
from Model.Content.CombatModifiers import (
    Movement,
    modifier_from_dict,
    modifier_to_dict,
)

CORRIDOR = ArenaSettings(width=10, height=1)


def _feat(cls, ability: Ability):
    """A Level 4+ feat taken at level 4, its +1 to `ability`."""
    return cls(4, ability)


def _monster(name: str, at=None, size: str = "Medium", **keys: Any) -> dict:
    char = {"name": name, "size": size, "hp": 7, "speed_ground_ft": 30, **keys}
    if at is not None:
        char["position"] = list(at)
    return char


def _player(name: str, at=None, *features, **keys: Any) -> dict:
    char = {
        "name": name,
        "_is_player": True,
        "size": "Medium",
        "hp": 20,
        "speed": 30,
        "conditions": [],
        "_feature_objects": list(features),
    }
    char.update(keys)
    if at is not None:
        char["position"] = list(at)
    return char


def _with_badge(char: dict, name: str, *modifiers) -> dict:
    char.setdefault("conditions", []).append(name)
    give_modifiers(char, name, modifiers)
    return char


# ---------------------------------------------------------------------------
# The modifier


def test_a_movement_round_trips_as_a_log_keeps_it():
    for movement in (
        Movement(past_larger=True),
        Movement(ignores_difficult=True, after="Dash"),
        Movement(climbs=True, stands_up_ft=5),
        Movement(through_creatures=True, through_objects=True),
    ):
        assert modifier_from_dict(modifier_to_dict(movement)) == movement


@pytest.mark.parametrize(
    "keys",
    [{}, {"after": "Dash"}, {"ignores_difficult": True, "after": "Hide"}],
    ids=["no rule", "after without ignoring", "an unknown action"],
)
def test_a_movement_that_says_nothing_or_nonsense_is_refused(keys):
    with pytest.raises(ValueError):
        Movement(**keys)


# ---------------------------------------------------------------------------
# Halfling Nimbleness: "move through the space of any creature that is a
# size larger than you, but you can't stop in the same space"


def test_a_halfling_moves_through_a_larger_enemy_but_cant_stop_there():
    goblin = _monster("Bandit", (1, 0))  # Medium: one size larger
    plain = _player("Halfling", (0, 0), size="Small")
    assert Cell(2, 0) not in reachable(plain, [plain, goblin], CORRIDOR, 30)

    halfling = _player("Halfling", (0, 0), HalflingNimbleness(), size="Small")
    reach = reachable(halfling, [halfling, goblin], CORRIDOR, 30)
    assert Cell(1, 0) not in reach, "can't stop in the same space"
    # The Bandit's space is still Difficult Terrain: 10, then 5 out.
    assert reach[Cell(2, 0)] == 15
    assert not can_end_at(halfling, Cell(1, 0), [halfling, goblin], CORRIDOR)


def test_nimbleness_doesnt_pass_a_creature_its_own_size():
    goblin = _monster("Goblin", (1, 0), "Small")
    halfling = _player("Halfling", (0, 0), HalflingNimbleness(), size="Small")
    assert Cell(2, 0) not in reachable(halfling, [halfling, goblin], CORRIDOR, 30)


# ---------------------------------------------------------------------------
# Incorporeal Movement: "move through other creatures and objects as if they
# were Difficult Terrain. It takes 5 (1d10) Force damage if it ends its turn
# inside an object."

_INCORPOREAL = [{"name": "Incorporeal Movement", "description": "..."}]


def test_a_ghost_moves_through_creatures_and_walls_as_difficult_terrain():
    settings = ArenaSettings(width=10, height=1)
    settings.terrain.put(Cell(3, 0), Spot(ground=WALL))
    fighter = _player("Fighter", (1, 0))
    ghost = _monster("Ghost", (0, 0), traits=_INCORPOREAL)
    reach = reachable(ghost, [ghost, fighter], settings, 30)
    assert Cell(1, 0) not in reach, "it can't end a move on a creature"
    assert reach[Cell(2, 0)] == 15
    assert reach[Cell(3, 0)] == 25, "inside the wall, where a move can end"
    assert reach[Cell(4, 0)] == 30
    assert can_end_at(ghost, Cell(3, 0), [ghost, fighter], settings)

    goblin = _monster("Goblin", (0, 0))
    assert Cell(2, 0) not in reachable(goblin, [goblin, fighter], settings, 30)
    assert not can_end_at(goblin, Cell(3, 0), [goblin, fighter], settings)


# ---------------------------------------------------------------------------
# Swarm: "can occupy another creature's space and vice versa"

_SWARM = [{"name": "Swarm", "description": "..."}]


def test_a_swarm_ends_its_move_on_a_creature_and_a_creature_on_it():
    fighter = _player("Fighter", (1, 0))
    rats = _monster("Swarm of Rats", (3, 0), traits=_SWARM)
    swarm_reach = reachable(rats, [rats, fighter], CORRIDOR, 30)
    assert swarm_reach[Cell(1, 0)] == 15, "into the Fighter's space, Difficult"
    fighter_reach = reachable(fighter, [fighter, rats], CORRIDOR, 30)
    assert fighter_reach[Cell(3, 0)] == 15, "onto the swarm: 5 + 10"
    assert can_end_at(fighter, Cell(3, 0), [fighter, rats], CORRIDOR)


# ---------------------------------------------------------------------------
# Difficult Terrain that costs nothing extra


def _rubble_and_an_enemy() -> tuple[ArenaSettings, dict]:
    settings = ArenaSettings(width=10, height=1)
    settings.terrain.put(Cell(1, 0), Spot(ground=DIFFICULT))
    return settings, _monster("Goblin", (3, 0), "Medium")


def test_freedom_of_movement_ignores_difficult_terrain_and_enemy_spaces():
    """Freedom of Movement: "movement is unaffected by Difficult Terrain"; an
    enemy's space is Difficult Terrain (Rules Glossary). The badge is the
    one the spell's combat effect gives."""
    settings, goblin = _rubble_and_an_enemy()
    goblin["size"] = "Tiny"  # passed, and its space isn't Difficult anyway
    cleric = _player("Cleric", (0, 0))
    assert move_cost(cleric, [cleric, goblin], settings, Cell(2, 0)) == 15
    (badge,) = FreedomOfMovement().combat_effects()[0].conditions
    _with_badge(cleric, badge.name, *badge.modifiers)
    assert move_cost(cleric, [cleric, goblin], settings, Cell(2, 0)) == 10

    bear = _monster("Bear", (3, 0), "Large")
    halfling = _player("Halfling", (2, 0), size="Small")
    _with_badge(halfling, badge.name, *badge.modifiers)
    # Small and Large are two sizes apart, so it passes the Bear's space (2
    # cells on this one-row map), at no extra cost: 3 steps.
    assert move_cost(halfling, [halfling, bear], CORRIDOR, Cell(5, 0)) == 15


def test_speedy_ignores_difficult_terrain_only_after_a_dash():
    settings, _ = _rubble_and_an_enemy()
    runner = _player("Runner", (0, 0), _feat(Speedy, Ability.DEXTERITY))
    assert move_cost(runner, [runner], settings, Cell(2, 0)) == 15
    runner["dashes"] = 1
    assert move_cost(runner, [runner], settings, Cell(2, 0)) == 10


def test_fairy_trickster_ignores_difficult_terrain_after_a_disengage():
    settings, _ = _rubble_and_an_enemy()
    fey = _player("Fey", (0, 0), _feat(FairyTrickster, Ability.CHARISMA))
    assert move_cost(fey, [fey], settings, Cell(2, 0)) == 15
    fey["conditions"].append("Disengage")
    assert move_cost(fey, [fey], settings, Cell(2, 0)) == 10
    assert not movement_rules(
        _player("Plain", conditions=["Disengage"])
    ).ignores_difficult


# ---------------------------------------------------------------------------
# Climbing at no extra cost: "a Climb Speed equal to your Speed"


def test_athlete_and_spider_climb_climb_a_ledge_at_no_extra_cost():
    """A 5-ft. step onto a 10-ft. ledge is 5 + 10 x 2 walking (test
    test_a_step_up_a_ledge_is_a_climb), 5 + 10 with a Climb Speed."""
    settings = ArenaSettings(width=10, height=1)
    settings.terrain.put(Cell(1, 0), Spot(height_ft=10))
    walker = _player("Walker", (0, 0))
    assert move_cost(walker, [walker], settings, Cell(1, 0)) == 25
    athlete = _player("Athlete", (0, 0), _feat(Athlete, Ability.STRENGTH))
    assert move_cost(athlete, [athlete], settings, Cell(1, 0)) == 15
    (badge,) = SpiderClimb().combat_effects()[0].conditions
    _with_badge(walker, badge.name, *badge.modifiers)
    assert move_cost(walker, [walker], settings, Cell(1, 0)) == 15


# ---------------------------------------------------------------------------
# Standing up: "spend an amount of movement equal to half your Speed (round
# down) to right yourself"


def test_standing_up_costs_half_the_speed_or_5_feet_with_hop_up():
    assert stand_up_ft(_player("Fighter", speed=30)) == 15
    assert stand_up_ft(_player("Dwarf", speed=25)) == 12, "rounded down"
    assert (
        stand_up_ft(
            _player("Athlete", None, _feat(Athlete, Ability.STRENGTH), speed=30)
        )
        == 5
    )
    assert (
        stand_up_ft(_player("Slow", None, _feat(Athlete, Ability.STRENGTH), speed=5))
        == 2
    ), "never more"
    assert stand_up_ft(_monster("Goblin")) == 15
