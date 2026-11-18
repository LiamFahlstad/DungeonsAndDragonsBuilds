"""Where a push or a pull leaves a creature (Combat/Arena/pushes.py,
Notes/combat-arena-plan.md step 21, Decision 32), on plain combatant dicts,
and CombatEffect's `push` (Model/Content/CombatEffect.py).

Rules Glossary, Unarmed Strike: a Shove pushes the target "5 feet away";
Thunderwave: "pushed 10 feet away from you"; the Push mastery: "push the
creature up to 10 feet straight away from yourself if it is Large or
smaller"."""

import pytest

from Combat.Arena.arena import ArenaSettings
from Combat.Arena.geometry import Cell
from Combat.Arena.pushes import PushResult, push_destination, push_order, too_big
from Combat.Arena.terrain import WALL, Spot
from Core.Definitions import CreatureSize
from Model.Content.CombatEffect import CombatEffect, CombatPush


def _char(name: str, col: int, row: int, **extra) -> dict:
    return {"name": name, "position": [col, row], "conditions": [], "hp": 10, **extra}


def _push(target, pusher, push, *others, settings=None):
    settings = settings or ArenaSettings()
    return push_destination(target, pusher, push, [pusher, target, *others], settings)


def test_a_push_along_a_row_stays_on_it():
    pusher, goblin = _char("Edmund", 2, 5), _char("Goblin", 3, 5)
    assert _push(goblin, pusher, CombatPush(10)) == PushResult(Cell(5, 5), 10)


def test_a_push_goes_away_from_the_pusher_whichever_side_it_is_on():
    pusher = _char("Edmund", 5, 5)
    assert _push(_char("G", 5, 4), pusher, CombatPush(5)).to == Cell(5, 3)
    assert _push(_char("G", 4, 5), pusher, CombatPush(5)).to == Cell(3, 5)


def test_a_diagonal_push_is_a_staircase_along_the_diagonal():
    """Each 5 feet is one step farther away by the Manhattan rule, kept
    nearest the line from the pusher through the target: 20 feet from one
    cell off diagonally is two cells right and two down."""
    pusher, goblin = _char("Edmund", 2, 5), _char("Goblin", 3, 6)
    result = _push(goblin, pusher, CombatPush(20))
    assert result == PushResult(Cell(5, 8), 20)


def test_a_push_stops_short_of_someone_else():
    pusher, goblin = _char("Edmund", 2, 5), _char("Goblin", 3, 5)
    orc = _char("Orc", 5, 5)
    result = _push(goblin, pusher, CombatPush(15), orc)
    assert result == PushResult(Cell(4, 5), 5, "Orc's space")


def test_a_push_stops_at_a_wall_and_at_the_maps_edge():
    settings = ArenaSettings()
    settings.terrain.put(Cell(5, 5), Spot(ground=WALL))
    pusher, goblin = _char("Edmund", 2, 5), _char("Goblin", 3, 5)
    result = _push(goblin, pusher, CombatPush(15), settings=settings)
    assert result == PushResult(Cell(4, 5), 5, "a wall or an object")
    edge = settings.width - 2
    near_edge = _char("Goblin", edge, 5)
    result = _push(near_edge, _char("Edmund", edge - 1, 5), CombatPush(15))
    assert result == PushResult(Cell(edge + 1, 5), 5, "the map's edge")


def test_a_large_creature_is_pushed_whole():
    """A Large Tiger covers 2 by 2 cells: its anchor moves, and its cells
    all have to fit."""
    pusher, tiger = _char("Edmund", 5, 5), _char("Tiger", 6, 5, size="Large")
    assert _push(tiger, pusher, CombatPush(10)) == PushResult(Cell(8, 5), 10)
    orc = _char("Orc", 9, 6)  # in the way of its lower row only
    assert _push(tiger, pusher, CombatPush(10), orc).stopped_by == "Orc's space"


def test_a_pull_comes_toward_the_puller_and_stops_next_to_it():
    puller, goblin = _char("Druid", 2, 5), _char("Goblin", 6, 5)
    assert _push(goblin, puller, CombatPush(10, toward=True)) == PushResult(
        Cell(4, 5), 10
    )
    pulled_far = _push(goblin, puller, CombatPush(30, toward=True))
    assert pulled_far == PushResult(Cell(3, 5), 15), "next to the puller"


def test_no_push_off_the_map_or_from_the_same_space():
    pusher, goblin = _char("Edmund", 2, 5), _char("Goblin", 3, 5)
    off = {"name": "Off", "conditions": [], "hp": 10}
    assert _push(off, pusher, CombatPush(10)) is None
    assert _push(goblin, off, CombatPush(10)) is None
    swarm = _char("Swarm", 3, 5)
    assert _push(goblin, swarm, CombatPush(10)) is None, "no 'away' to push"


def test_too_big_is_by_the_size_in_use():
    push = CombatPush(10, up_to=True, largest=CreatureSize.LARGE)
    assert not too_big({"size": "Large"}, push)
    assert too_big({"size": "Huge"}, push)
    assert not too_big({}, push), "a size not known is the GM's"
    assert not too_big({"size": "Gargantuan"}, CombatPush(10))


def test_the_farthest_is_pushed_first_and_the_nearest_pulled_first():
    pusher = _char("Edmund", 2, 5)
    near, far = _char("Near", 3, 5), _char("Far", 4, 5)
    off = {"name": "Off", "conditions": [], "hp": 10}
    settings = ArenaSettings()
    assert push_order([near, off, far], pusher, CombatPush(5), settings) == [
        far,
        near,
        off,
    ]
    pull = CombatPush(5, toward=True)
    assert push_order([far, near], pusher, pull, settings) == [near, far]


def test_combat_push_text_and_checks():
    assert CombatPush(10).text == "pushed 10 ft."
    assert CombatPush(10, up_to=True).text == "pushed up to 10 ft."
    assert CombatPush(10, toward=True).text == "pulled 10 ft."
    for feet in (0, 7, True, "10"):
        with pytest.raises(ValueError):
            CombatPush(feet)
    assert CombatPush(5, largest="Large").largest is CreatureSize.LARGE
    with pytest.raises(ValueError):
        CombatEffect(targets_self=True, push=CombatPush(5))


def test_a_push_is_kept_and_read_back():
    effect = CombatEffect(
        push=CombatPush(10, up_to=True, toward=True, largest=CreatureSize.LARGE)
    )
    data = effect.to_dict()
    assert data == {
        "push": {"feet": 10, "up_to": True, "toward": True, "largest": "Large"}
    }
    assert CombatEffect.from_dict(data) == effect
    assert CombatEffect.from_dict({}).push is None
    with pytest.raises(ValueError, match="push"):
        CombatEffect.from_dict({"push": {"feet": 10, "far": True}})
