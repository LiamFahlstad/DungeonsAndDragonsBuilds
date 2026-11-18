"""Light and senses in the combat window (Notes/combat-arena-plan.md, step
28): once the battle map is in use, a target in painted Darkness the
attacker can't see into gives its attack Disadvantage (Rules Glossary,
Heavily Obscured: Blinded while trying to see there), an Invisible one
(the GM's visibility state, DI-068) too, and the target's label says who
can't see it."""

import random

import pytest

from Combat.Arena.arena import POSITION_KEY
from Combat.Arena.geometry import Cell
from Combat.Arena.terrain import DARK
from Combat.Combatants import Pirate, Tiger
from Combat.CombatUIQt.effect_options import MONSTER_ACTION
from Combat.CombatUIQt.monster_actions import DamageRoll, MonsterAction
from Combat.CombatUIQt.saves import ATTACK_ROLL, CustomEffect, EffectOption
from Core.Definitions import DamageType
from Model.Creatures.Combatants import Visibility
from tests._combat_ui import make_ui

CLAWS = MonsterAction(
    "Claws",
    "Melee Attack Roll: +0, reach 5 ft. Hit: 5 Slashing damage.",
    to_hit=0,
    damage=(DamageRoll("1d6", "Slashing"),),
)
PICK = EffectOption(
    name="Claws", kind=MONSTER_ACTION, roll=ATTACK_ROLL, monster_action=CLAWS
)


@pytest.fixture
def fight(tmp_path, monkeypatch):
    """The Pirate (the source, on its turn) at A1 beside the Tiger, AC 10,
    at B1, on a map in use; neither has a special sense. The d20s roll 15
    then 4: a hit rolled straight, a miss with Disadvantage."""
    ui = make_ui(tmp_path, [Pirate(), Tiger()])
    pirate, tiger = ui.characters
    for char, value in zip(ui.characters, (15, 10)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    ui._select_target_character(tiger)
    pirate[POSITION_KEY] = [0, 0]
    tiger[POSITION_KEY] = [1, 0]
    tiger["ac"] = 10
    ui.arena_settings.in_use = True
    rolls = iter((15, 4))
    monkeypatch.setattr(random, "randint", lambda low, high: next(rolls, 3))
    return ui, pirate, tiger


def _claw(ui):
    ui._apply_custom_effect(
        CustomEffect(damage=[(5, DamageType.SLASHING.value)], attack_bonus=0, pick=PICK)
    )


def test_in_the_light_the_claws_hit(fight):
    ui, _, tiger = fight
    _claw(ui)
    assert tiger["hp"] < tiger["max_hp"]


def test_a_tiger_in_darkness_is_clawed_at_with_disadvantage(fight):
    ui, _, tiger = fight
    ui.arena_settings.terrain.change(Cell.of([1, 0]), light=DARK)
    assert "Pirate can't see it: Darkness at B1" in ui._distance_note(tiger)
    _claw(ui)
    assert tiger["hp"] == tiger["max_hp"]
    assert "Pirate can't see Tiger (Darkness at B1): Disadvantage" in str(
        ui._read_log()
    )


def test_an_invisible_tiger_is_clawed_at_with_disadvantage(fight):
    ui, _, tiger = fight
    tiger["visibility_states"] = [Visibility.INVISIBLE.value]
    assert "Pirate can't see it: Tiger is Invisible" in ui._distance_note(tiger)
    _claw(ui)
    assert tiger["hp"] == tiger["max_hp"]


def test_before_the_map_is_in_use_nothing_is_counted(fight):
    ui, _, tiger = fight
    ui.arena_settings.in_use = False
    ui.arena_settings.terrain.change(Cell.of([1, 0]), light=DARK)
    _claw(ui)
    assert tiger["hp"] < tiger["max_hp"]
