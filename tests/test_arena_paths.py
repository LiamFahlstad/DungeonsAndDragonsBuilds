"""The way a walk goes on the battle map, and whose reach it passes
(Notes/combat-arena-plan.md step 23; Combat/Arena/arena.py), on plain
combatant dicts.

Rules Glossary, Opportunity Attacks: "when a creature that you can see
leaves your reach". Polearm Master (Player's Handbook), Reactive Strike: "a
Reaction to make one melee attack against a creature that enters the reach
you have with that weapon"."""

from CharacterContent.Items.Weapons.MartialMelee import Glaive
from CharacterContent.Features.CharacterFeats.GeneralFeats import PolearmMaster
from CharacterContent.Items.Weapons.SimpleMelee import Javelin, Quarterstaff, Spear
from Combat.Arena.arena import (
    ArenaSettings,
    opportunity_attackers,
    position,
    reactive_strikers,
    walk_path,
)
from Combat.Arena.geometry import Cell
from Combat.Arena.terrain import WALL, Spot
from Core.Definitions import Ability


def _char(name: str, col: int, row: int = 5, **extra) -> dict:
    return {
        "name": name,
        "position": [col, row],
        "conditions": [],
        "hp": 10,
        "speed": 30,
        **extra,
    }


def _walk(mover: dict, to: Cell, chars: list[dict], settings=None) -> list[Cell]:
    """Walk mover to `to` (its path), as the window does."""
    settings = settings or ArenaSettings()
    path = walk_path(mover, chars, settings, to)
    assert path is not None
    mover["position"] = to.to_list()
    return path


def test_the_path_starts_where_it_is_and_ends_where_it_goes():
    edmund = _char("Edmund", 2, _is_player=True)
    path = walk_path(edmund, [edmund], ArenaSettings(), Cell(5, 5))
    assert path == [Cell(2, 5), Cell(3, 5), Cell(4, 5), Cell(5, 5)]
    assert walk_path(edmund, [edmund], ArenaSettings(), Cell(2, 5)) == [Cell(2, 5)]


def test_the_path_goes_round_a_wall():
    settings = ArenaSettings()
    settings.terrain.put(Cell(3, 5), Spot(ground=WALL))
    edmund = _char("Edmund", 2, _is_player=True)
    path = walk_path(edmund, [edmund], settings, Cell(4, 5))
    assert path is not None
    assert Cell(3, 5) not in path
    assert len(path) == 5, "round the wall: 4 steps"
    walled = _char("Walled", 0)
    settings.terrain.put(Cell(1, 5), Spot(ground=WALL))
    settings.terrain.put(Cell(0, 4), Spot(ground=WALL))
    settings.terrain.put(Cell(0, 6), Spot(ground=WALL))
    assert walk_path(walled, [walled], settings, Cell(5, 5)) is None


def test_walking_past_an_enemy_provokes_though_both_ends_are_out_of_reach():
    """Two cells above the goblin to two cells below it, through the cell
    beside it: in its reach on the way, out of it at the end."""
    settings = ArenaSettings()
    edmund = _char("Edmund", 4, 3, _is_player=True)
    goblin = _char("Goblin", 5, 4)
    path = [Cell(4, 3), Cell(4, 4), Cell(4, 5), Cell(4, 6)]
    edmund["position"] = [4, 6]
    start = path[0]
    assert opportunity_attackers(edmund, start, [edmund, goblin], settings) == []
    assert opportunity_attackers(edmund, start, [edmund, goblin], settings, path) == [
        goblin
    ]


def test_staying_in_reach_all_the_way_provokes_nothing():
    settings = ArenaSettings()
    edmund = _char("Edmund", 5, _is_player=True)
    tiger = _char("Tiger", 6, size="Large")
    path = _walk(edmund, Cell(5, 6), [edmund, tiger], settings)
    assert opportunity_attackers(edmund, path[0], [edmund, tiger], settings, path) == []


def test_a_used_reaction_or_an_ally_makes_no_opportunity_attack():
    settings = ArenaSettings()
    edmund = _char("Edmund", 4, 3, _is_player=True)
    goblin = _char("Goblin", 5, 4, action_uses={"Reaction": 1})
    friend = _char("Friend", 5, 4, _is_player=True)
    path = [Cell(4, 3), Cell(4, 4), Cell(4, 5), Cell(4, 6)]
    edmund["position"] = [4, 6]
    for other in (goblin, friend):
        assert (
            opportunity_attackers(edmund, path[0], [edmund, other], settings, path)
            == []
        )


def _polearm_master(name: str, col: int, row: int, weapon) -> dict:
    return _char(
        name,
        col,
        row,
        _is_player=True,
        _feature_objects=[PolearmMaster(4, Ability.STRENGTH)],
        _weapons_objects=[weapon],
    )


def test_entering_a_polearm_masters_reach_offers_its_reactive_strike():
    settings = ArenaSettings()
    kivi = _polearm_master("Kivi", 8, 5, Spear())
    goblin = _char("Goblin", 4)
    path = _walk(goblin, Cell(7, 5), [kivi, goblin], settings)
    assert reactive_strikers(goblin, path, [kivi, goblin], settings) == [kivi]
    # Already inside, and staying: it didn't enter.
    path = _walk(goblin, Cell(7, 6), [kivi, goblin], settings)
    assert path[0] == Cell(7, 5)
    assert reactive_strikers(goblin, path, [kivi, goblin], settings) == []


def test_a_heavy_reach_polearm_reaches_10_feet_and_others_dont_count():
    settings = ArenaSettings()
    kivi = _polearm_master("Kivi", 8, 5, Glaive())
    goblin = _char("Goblin", 4)
    path = _walk(goblin, Cell(6, 5), [kivi, goblin], settings)
    assert reactive_strikers(goblin, path, [kivi, goblin], settings) == [kivi]
    assert position(goblin) == Cell(6, 5)
    staff = _polearm_master("Staff", 8, 5, Quarterstaff())
    no_feat = _char("Plain", 8, 5, _is_player=True, _weapons_objects=[Spear()])
    goblin["position"] = [4, 5]
    path = _walk(goblin, Cell(7, 5), [staff, goblin], settings)
    assert reactive_strikers(goblin, path, [staff, goblin], settings) == [staff]
    goblin["position"] = [4, 5]
    path = _walk(goblin, Cell(7, 5), [no_feat, goblin], settings)
    assert reactive_strikers(goblin, path, [no_feat, goblin], settings) == []
    javelin = _polearm_master("Javelin", 8, 5, Javelin())
    goblin["position"] = [4, 5]
    path = _walk(goblin, Cell(7, 5), [javelin, goblin], settings)
    assert reactive_strikers(goblin, path, [javelin, goblin], settings) == []
