"""Rows the model could already say (Notes/combat-effects-plan.md, step 9.1):
a spell's later step as a row of its own, a Swim Speed, a push each way.

Expected values are the rules text's:

- Spiritual Weapon: "On each of your later turns, you can take a Bonus
  Action to move the force up to 20 feet and repeat the attack against a
  creature within 5 feet of it."
- Produce Flame: casting time a Bonus Action; "Until the spell ends, the
  flame emits Bright Light in a 20-foot radius and Dim Light for an
  additional 20 feet. The spell ends if you cast it again. As a Magic
  action, you can hurl the flame".
- Freedom of Movement: "It also has a Swim Speed equal to its Speed."
- Elemental Strikes (Warrior of the Elements): "On a failed save, you can
  move the target up to 10 feet toward or away from you."
"""

from typing import cast

import pytest

from CharacterContent.Features.SubClassFeatures.Monk.MonkElementsFeatures import (
    ElementalAttunement,
)
from CharacterContent.Spells.SpellFactory import SpellFactory
from Combat.Definitions import ActionCost
from Combat.Fight.effect_options import spell_options
from Combat.Fight.saves import ATTACK_ROLL
from Core.Definitions import Ability
from Model.Content.ActionType import ActionType
from Model.Content.CombatEffect import CombatPush
from Model.Content.CombatModifiers import Movement
from Model.View import CharacterView

NO_SHEET = cast(CharacterView, None)


def _rows(spell: str) -> dict:
    return {o.name: o for o in spell_options(SpellFactory.create(spell), None)}


def test_spiritual_weapons_later_attack_costs_a_bonus_action_and_no_slot():
    rows = _rows("Spiritual Weapon")
    cast_row = next(o for o in rows.values() if o.counts_uses)
    again = rows["Spiritual Weapon: attack again"]
    assert again.roll == cast_row.roll == ATTACK_ROLL
    assert again.damage_at(None) == cast_row.damage_at(None)
    assert again.action_cost == ActionCost.BONUS_ACTION
    assert not again.counts_uses and again.slot_level is None


def test_produce_flame_is_cast_as_a_flame_then_hurled_as_a_magic_action():
    effects = SpellFactory.create("Produce Flame").combat_effects()
    assert effects is not None
    cast_effect, hurl = effects
    # Casting it puts the flame in its caster's hand, for 10 minutes.
    assert cast_effect.targets_self and cast_effect.spends_use
    (flame,) = cast_effect.conditions
    assert (flame.name, flame.duration_seconds) == ("Produce Flame", 600)
    # Hurling it: the attack, a Magic action, no new casting.
    assert hurl.name == "Produce Flame: hurl"
    assert hurl.action_type is ActionType.ACTION and not hurl.spends_use
    rows = _rows("Produce Flame")
    assert rows["Produce Flame: hurl"].action_cost == ActionCost.ACTION
    assert not rows["Produce Flame: hurl"].counts_uses


def test_freedom_of_movement_gives_a_swim_speed_equal_to_its_speed():
    effects = SpellFactory.create("Freedom of Movement").combat_effects()
    assert effects is not None
    ((badge,),) = [e.conditions for e in effects]
    movements = [m for m in badge.modifiers if isinstance(m, Movement)]
    assert movements == [Movement(ignores_difficult=True, swims=True)]


@pytest.mark.parametrize(
    "way, toward",
    [("away", False), ("toward", True)],
)
def test_elemental_strikes_moves_the_target_up_to_10_feet_each_way(way, toward):
    rows = {e.name: e for e in ElementalAttunement().combat_effects(NO_SHEET)}
    row = rows[f"Elemental Strikes: move {way}"]
    assert row.save_ability is Ability.STRENGTH and not row.spends_use
    assert row.push == CombatPush(10, up_to=True, toward=toward)
