"""Reach and range from the battle map in the combat window
(Notes/combat-arena-plan.md, step 20): a ranged attack past its normal
range, or with an enemy within 5 feet, has Disadvantage (Player's Handbook,
Range; Ranged Attacks in Close Combat), counted in the Use / Cast dialog's
roll and a monster's button; one past its reach or long range is warned
about, not refused. Nothing counts before the map is in use (Decision 29)."""

import random

import pytest

from Combat.Arena.arena import POSITION_KEY
from Combat.Arena.ranges import AttackRange, check_attack_range
from Combat.Combatants import Pirate, Tiger
from Combat.PartyAllies import ENCOUNTER_ALLY_KEY
from Combat.CombatUIQt.use_cast.dialog import _attack_text
from Combat.Fight.effect_options import MONSTER_ACTION, pick_attack_range
from Combat.Fight.monster_actions import DamageRoll, MonsterAction
from Combat.Fight.saves import ATTACK_ROLL, CustomEffect, EffectOption
from Core.Definitions import DamageType
from tests._combat_ui import make_ui

PIERCING = DamageType.PIERCING.value
# Their reach and range are fields (stated_range), as an attack effect's
# reach_ft / range_ft give them; the text is only shown.
SHORTBOW = MonsterAction(
    "Shortbow",
    "Ranged Attack Roll: +0, range 20/60 ft. Hit: 5 (1d6 + 2) Piercing damage.",
    to_hit=0,
    damage=(DamageRoll("1d6 + 2", "Piercing"),),
    stated_range=(None, 20, 60),
)
CLAWS = MonsterAction(
    "Claws",
    "Melee Attack Roll: +0, reach 5 ft. Hit: 5 Slashing damage.",
    to_hit=0,
    damage=(DamageRoll("1d6", "Slashing"),),
    stated_range=(5, None, None),
)


def _pick(action: MonsterAction) -> EffectOption:
    return EffectOption(
        name=action.name, kind=MONSTER_ACTION, roll=ATTACK_ROLL, monster_action=action
    )


@pytest.fixture
def fight(tmp_path):
    """The Pirate (the source, whose turn it is) at A1, the Tiger, AC 10, at
    F1 (25 ft.), on a map in use."""
    ui = make_ui(tmp_path, [Pirate(), Tiger()])
    pirate, tiger = ui.characters
    for char, value in zip(ui.characters, (15, 10)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    ui._select_target_character(tiger)
    pirate[POSITION_KEY] = [0, 0]
    tiger[POSITION_KEY] = [5, 0]
    tiger["ac"] = 10
    ui.arena_settings.in_use = True
    return ui, pirate, tiger


def _d20s(monkeypatch, *rolls: int):
    results = iter(rolls)
    monkeypatch.setattr(random, "randint", lambda low, high: next(results, 3))


def _log(ui) -> str:
    return str(ui._read_log())


def _shoot(ui):
    ui._apply_custom_effect(
        CustomEffect(damage=[(5, PIERCING)], attack_bonus=0, pick=_pick(SHORTBOW))
    )


def test_a_shot_past_the_normal_range_has_disadvantage(fight, monkeypatch):
    ui, _, tiger = fight
    _d20s(monkeypatch, 15, 4)  # Disadvantage keeps the 4: a miss
    _shoot(ui)
    assert tiger["hp"] == tiger["max_hp"]
    assert "Long range, 25 ft. of 20/60 ft.: Disadvantage" in _log(ui)


def test_within_the_normal_range_its_a_straight_roll(fight, monkeypatch):
    ui, _, tiger = fight
    tiger[POSITION_KEY] = [3, 0]  # 15 ft.
    _d20s(monkeypatch, 15, 4)
    _shoot(ui)
    assert tiger["hp"] == tiger["max_hp"] - 5


def test_before_the_map_is_in_use_the_range_counts_nothing(fight, monkeypatch):
    ui, _, tiger = fight
    ui.arena_settings.in_use = False
    _d20s(monkeypatch, 15, 4)
    _shoot(ui)
    assert tiger["hp"] == tiger["max_hp"] - 5
    assert "Long range" not in _log(ui)


def test_a_shot_past_the_long_range_is_warned_about(fight, monkeypatch):
    ui, _, tiger = fight
    tiger[POSITION_KEY] = [13, 0]  # 65 ft.
    _d20s(monkeypatch, 15, 15)
    _shoot(ui)
    assert "Tiger is 65 ft. away, past its 20/60 ft. range" in _log(ui)


def test_a_claw_past_its_reach_is_warned_about_on_the_monsters_button(
    fight, monkeypatch
):
    ui, pirate, _ = fight
    _d20s(monkeypatch, 15, 15)
    ui._roll_action(CLAWS, pirate)
    assert "Tiger is 25 ft. away, past the 5 ft. reach" in (
        ui._action_result_label.text()
    )


def test_a_monsters_shot_with_an_enemy_beside_it_has_disadvantage(fight, monkeypatch):
    """The Tiger, fighting on the party's side, beside the Pirate: an enemy
    within 5 feet that can see it. (Two monsters are on the same side.)"""
    ui, pirate, tiger = fight
    tiger[ENCOUNTER_ALLY_KEY] = True
    tiger[POSITION_KEY] = [1, 0]
    _d20s(monkeypatch, 15, 4)  # the 4 is kept: 4 misses AC 10
    ui._roll_action(SHORTBOW, pirate)
    text = ui._action_result_label.text()
    assert "MISS" in text
    assert "Ranged attack within 5 ft. of Tiger" in text


def test_the_dialogs_row_says_the_disadvantage_and_the_warning(fight):
    ui, pirate, tiger = fight
    attack = pick_attack_range(_pick(SHORTBOW), pirate)
    assert attack == AttackRange(normal_ft=20, long_ft=60, what="Shortbow")
    long = check_attack_range(attack, pirate, tiger, ui.characters, ui.arena_settings)
    assert _attack_text(pirate, tiger, reach=long) == "AC 10, Disadvantage"
    tiger[POSITION_KEY] = [13, 0]
    past = check_attack_range(attack, pirate, tiger, ui.characters, ui.arena_settings)
    assert _attack_text(pirate, tiger, reach=past) == (
        "AC 10; past its 20/60 ft. range"
    )


def test_another_monster_beside_it_is_no_enemy(fight, monkeypatch):
    ui, pirate, tiger = fight
    tiger[POSITION_KEY] = [1, 0]
    _d20s(monkeypatch, 15, 4)
    ui._roll_action(SHORTBOW, pirate)
    assert "HIT" in ui._action_result_label.text()
