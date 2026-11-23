"""A short rest without the combat window (Combat/Fight/rests.py,
Notes/combat-ui-refactor-plan.md step 5.3): Pact Magic slots come back on a
short rest (Warlock, Pact Magic), Wild Shape gets one expended use back
(Druid, Wild Shape), and Hit Dice heal a creature that isn't dead, outside
the fight's statistics."""

from functools import cache

from Combat.Fight.rests import (
    SHORT_REST_CADENCES,
    heal_with_hit_dice,
    regain_feature_uses,
    regain_pact_slots,
)
from Combat.PlayerCombatant import combatant_from_character
from tests._snapshot_helpers import build

# Warlock 3: two level 2 Pact Magic slots.
WARLOCK = "Y2024WarlockArchfeyThistleFeydreamCharacterBuilder"
# Circle of the Moon Druid 3: two uses of Wild Shape.
MOON = "Y2024DruidMoonBriarWolfshadeCharacterBuilder"


@cache
def _sheet(name: str):
    return build(name)


def _player(name: str) -> dict:
    return combatant_from_character(_sheet(name))


def test_a_short_rest_gives_back_each_pact_magic_slot_spent():
    warlock = _player(WARLOCK)
    warlock["pact_slots"] = {2: 0}
    assert regain_pact_slots(warlock) == [2, 2]
    assert warlock["pact_slots"] == {2: 2}
    assert regain_pact_slots(warlock) == []


def test_wild_shape_gets_one_expended_use_back_on_a_short_rest():
    druid = _player(MOON)
    druid["feature_uses_used"] = {"Wild Shape": 2}
    regained = regain_feature_uses(druid, SHORT_REST_CADENCES, "short rest")
    assert regained.count("Wild Shape") == 1
    assert druid["feature_uses_used"]["Wild Shape"] == 1


def test_nothing_comes_back_without_a_sheet():
    goblin = {"name": "Goblin", "feature_uses_used": {"Nimble Escape": 1}}
    assert regain_feature_uses(goblin, SHORT_REST_CADENCES, "short rest") == []


def _hurt(hp: int, **keys) -> dict:
    return {
        "name": "Hanna",
        "hp": hp,
        "max_hp": 28,
        "temp_hp": 0,
        "conditions": [],
        "death_saves_fail": 0,
        "death_saves_success": 0,
        "_is_player": True,
        **keys,
    }


def test_hit_dice_heal_up_to_the_maximum_outside_the_statistics():
    hanna = _hurt(20)
    regained = heal_with_hit_dice(hanna, 12)
    assert regained is not None and regained.amount == 8
    assert hanna["hp"] == 28
    assert "stats" not in hanna or hanna["stats"].get("healing_received", 0) == 0


def test_hit_dice_bring_one_at_zero_hp_to():
    dying = _hurt(0, death_saves_fail=1, death_saves_success=2)
    regained = heal_with_hit_dice(dying, 5)
    assert regained is not None and regained.came_to
    assert (dying["death_saves_fail"], dying["death_saves_success"]) == (0, 0)


def test_the_dead_regain_nothing():
    dead = _hurt(0, death_saves_fail=3)
    assert heal_with_hit_dice(dead, 5) is None
    assert dead["hp"] == 0
