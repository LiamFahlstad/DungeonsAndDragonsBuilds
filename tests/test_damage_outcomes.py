"""Damage outcomes (Notes/combat-effects-plan.md, step 9.5): Evasion changes
what a Dexterity save for half damage does, Uncanny Dodge halves a hit's
damage, and a structured Regeneration is reminded of as its turn starts.

Expected values are the rules text's:

- Evasion (Rogue 7, Monk 7): "When you're subjected to an effect that
  allows you to make a Dexterity saving throw to take only half damage, you
  instead take no damage if you succeed on the saving throw and only half
  damage if you fail. You don't benefit from this feature if you have the
  Incapacitated condition."
- Uncanny Dodge (Rogue 5): "When an attacker that you can see hits you with
  an attack roll, you can take a Reaction to halve the attack's damage
  against you (round down)."
- Regeneration: "regains N Hit Points at the start of each of its turns".
"""

from typing import cast

import pytest
from PyQt6.QtWidgets import QDialog, QMessageBox

from Builds.Examples.Y2024_Rogue_Phantom_WraithGrimscar import (
    Y2024RoguePhantomWraithGrimscarCharacterBuilder as Wraith,
)
from CharacterContent.Features.ClassFeatures.Monk import MonkFeatures
from CharacterContent.Features.ClassFeatures.Rogue import RogueFeatures
from Combat.Combatants import Pirate, Tiger
from Combat.Effects.always_on import always_on_modifiers
from Combat.Effects.modifiers import held_conditions
from Combat.Effects.triggers import TriggerChoice
from Combat.Fight.attacks import Reduction, apply_reduction
from Combat.Fight.monster_actions import start_of_turn_traits
from Combat.Fight.saves import CustomEffect, evades
from Core.Definitions import Ability
from Model.Content.CombatEffect import HALF_DAMAGE, CombatEffect
from Model.Content.CombatModifiers import Evasion, modifier_from_dict, modifier_to_dict
from Model.Content.CombatTriggers import CombatTrigger, TriggerEvent
from Model.Creatures.MonsterAbilities import Regeneration
from Model.View import CharacterView
from tests._combat_ui import make_ui

NO_SHEET = cast(CharacterView, None)
FIREBALL = CustomEffect(
    name="Fireball", damage=[(20, "Fire")], ability="DEX", dc=15, half_on_save=True
)


# ---------------------------------------------------------------------------
# Evasion


def test_evasion_reads_back_and_is_a_dexterity_save_not_while_incapacitated():
    evasion = Evasion()
    assert (evasion.ability, evasion.unless_conditions) == (
        Ability.DEXTERITY,
        ("Incapacitated",),
    )
    assert modifier_from_dict(modifier_to_dict(evasion)) == evasion


@pytest.mark.parametrize("module", [RogueFeatures, MonkFeatures])
def test_the_rogues_and_monks_evasion_give_it_and_nothing_to_pick(module):
    feature = module.Evasion()
    assert feature.combat_modifiers(NO_SHEET) == (Evasion(),)
    assert feature.combat_effects(NO_SHEET) == []


def _evader(*conditions: str, **keys) -> dict:
    return {
        "name": "Tiger",
        "hp": 30,
        "max_hp": 30,
        "conditions": list(conditions),
        "traits": [{"name": "Evasion", "description": "..."}],
        **keys,
    }


def test_a_monsters_evasion_trait_gives_it():
    char = _evader()
    assert always_on_modifiers(char, held_conditions(char)) == [("Evasion", Evasion())]


def test_evasion_counts_on_a_dexterity_save_for_half_damage_only():
    char = _evader()
    assert evades(char, FIREBALL)
    wisdom = CustomEffect(damage=[(20, "Psychic")], ability="WIS", half_on_save=True)
    assert not evades(char, wisdom)
    no_half = CustomEffect(damage=[(20, "Fire")], ability="DEX", half_on_save=False)
    assert not evades(char, no_half)
    assert not evades({**char, "traits": []}, FIREBALL)


@pytest.mark.parametrize("held", ["Incapacitated", "Paralyzed"])
def test_evasion_is_lost_while_incapacitated(held):
    """Paralyzed gives Incapacitated, and with it the exception."""
    assert not evades(_evader(held), FIREBALL)


# ---------------------------------------------------------------------------
# Uncanny Dodge


def test_uncanny_dodge_is_a_reaction_that_halves_a_hit_it_sees():
    (effect,) = RogueFeatures.UncannyDodge().combat_effects(NO_SHEET)
    assert effect.damage_reduction == HALF_DAMAGE
    assert effect.trigger == CombatTrigger(TriggerEvent.HIT_BY, sees=True)
    with pytest.raises(ValueError):
        CombatEffect(damage_reduction="a third", trigger=effect.trigger)


def test_halving_rounds_each_damage_type_down_before_any_amount_off():
    parts = [(13, "Slashing"), (5, "Fire")]
    assert apply_reduction(parts, Reduction(0, halves=True)) == [
        (6, "Slashing"),
        (2, "Fire"),
    ]
    assert apply_reduction(parts, Reduction(7, halves=True)) == [(1, "Fire")]
    assert apply_reduction(parts, 3) == [(10, "Slashing"), (5, "Fire")]
    assert apply_reduction([(1, "Fire")], Reduction(0, halves=True)) == []


def test_a_halving_reduction_counts_as_one_even_with_nothing_off():
    assert Reduction(0, halves=True) and not Reduction(0) and Reduction(2) == 2


# ---------------------------------------------------------------------------
# Regeneration


def test_a_structured_regeneration_is_reminded_of_as_its_turn_starts():
    troll = {"traits": [Regeneration(creature_name="troll", hp=15)]}
    ((name, sentence),) = start_of_turn_traits(troll)
    assert name == "Regeneration"
    assert sentence.startswith("The troll regains 15 Hit Points at the start")


# ---------------------------------------------------------------------------
# In the window


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)
    monkeypatch.setattr(QMessageBox, "question", refuse)


@pytest.fixture
def fight(tmp_path, monkeypatch):
    """A Pirate (the source) and a Tiger (the target) with Evasion, on the
    Pirate's turn."""
    ui = make_ui(tmp_path, [Pirate(), Tiger()])
    pirate, tiger = ui.characters
    for char, value in zip(ui.characters, (15, 10)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    ui._select_character(pirate)
    ui._set_targets([tiger])
    tiger["traits"] = [*(tiger.get("traits") or []), {"name": "Evasion"}]
    tiger["Saving Throws"] = {"DEX": 0}
    return ui, pirate, tiger


def _lines(ui) -> list[str]:
    return [
        event["text"].split("] ", 1)[-1]
        for key, events in ui._read_log().items()
        if key.startswith("round_") and isinstance(events, list)
        for event in events
    ]


@pytest.mark.parametrize(
    "total, taken, said",
    [(30, 0, "no"), (1, 10, "half")],
    ids=["success: none", "failure: half"],
)
def test_evasion_on_a_fireball_save(fight, total, taken, said):
    ui, _, tiger = fight
    hp = tiger["hp"]
    ui._apply_custom_effect(
        CustomEffect(
            name="Fireball",
            damage=[(20, "Fire")],
            ability="DEX",
            dc=15,
            half_on_save=True,
            typed_totals={id(tiger): total},
        )
    )
    assert tiger["hp"] == hp - taken
    assert f"Tiger's Evasion: {said} damage" in _lines(ui)


def test_uncanny_dodge_halves_a_typed_hit(tmp_path, monkeypatch):
    """A Rogue 17 (Uncanny Dodge, Evasion) hit by the Pirate's typed attack
    asks about it, and Apply halves the 13 Slashing, spending its Reaction."""
    ui = make_ui(tmp_path, [Pirate()], [Wraith().build()])
    rogue, pirate = sorted(ui.characters, key=lambda c: not c.get("_is_player"))
    for char, value in ((pirate, 20), (rogue, 10)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    ui._select_character(pirate)
    asked: list[list[str]] = []

    def answer(firings):
        asked.append([f.row.name for f in firings])
        return TriggerChoice(apply=tuple(firings))

    monkeypatch.setattr(ui, "_ask_triggers", answer)
    hp = rogue["hp"]
    ui._set_targets([rogue])
    ui.attack_roll_input.setText("nat 20")
    ui.damage_input.setText("13 slashing")
    ui._apply_damage_checked()
    assert asked == [["Uncanny Dodge"]]
    assert rogue["hp"] == hp - 6  # 13 halved, rounded down
    assert f"{rogue['name']}'s Uncanny Dodge halves the damage" in _lines(ui)
    assert rogue["action_uses"]["Reaction"] == 1
