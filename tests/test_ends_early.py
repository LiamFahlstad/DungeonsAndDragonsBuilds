"""Badges that end early (Notes/combat-effects-plan.md, step 9.6, Decision
23): an EndsWhen modifier names what ends its badge, and the fight ends it
where it sees that happen, in the same undo step.

Expected values are the rules text's:

- Invisibility: "The spell ends early immediately after the target makes an
  attack roll, deals damage, or casts a spell."
- Sleep: "The spell ends on a target if it takes damage or someone within 5
  feet of it takes an action to shake it out of the spell's effect."
- Armor of Agathys: "The spell ends early if you have no Temporary Hit
  Points."
- Turn Undead: "These effects end early on the creature if it takes any
  damage".
- Elemental Attunement: "It ends early if you have the Incapacitated
  condition."
"""

from dataclasses import replace

import pytest
from PyQt6.QtWidgets import QDialog, QMessageBox

from CharacterContent.Spells.SpellFactory import SpellFactory
from Combat.Combatants import Pirate, Tiger
from Combat.Effects.active_effects import give_modifiers
from Combat.Fight.effect_options import spell_options
from Combat.Fight.picked import picked_effect
from Combat.Fight.saves import CustomEffect
from Model.Content.CombatModifiers import (
    EndEvent,
    EndsWhen,
    modifier_from_dict,
    modifier_to_dict,
)
from tests._combat_ui import make_ui

# ---------------------------------------------------------------------------
# The model


def test_ends_when_reads_back_and_needs_events():
    ends = EndsWhen((EndEvent.ATTACKS, EndEvent.CASTS_SPELL))
    assert modifier_from_dict(modifier_to_dict(ends)) == ends
    for bad in ((), ("attacks",)):
        with pytest.raises(ValueError):
            EndsWhen(bad)  # type: ignore[arg-type]


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
def fight(tmp_path):
    """A Pirate and a Tiger, on the Pirate's turn."""
    ui = make_ui(tmp_path, [Pirate(), Tiger()])
    pirate, tiger = ui.characters
    for char, value in zip(ui.characters, (15, 10)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    return ui, pirate, tiger


def _lines(ui) -> list[str]:
    return [
        event["text"].split("] ", 1)[-1]
        for key, events in ui._read_log().items()
        if key.startswith("round_") and isinstance(events, list)
        for event in events
    ]


def _cast(ui, caster, target, spell: str, **changes):
    """`spell` cast by caster on target, as its picker row is applied."""
    option = spell_options(SpellFactory.create(spell), caster)[0]
    effect = picked_effect(option, {})
    assert effect is not None
    ui._select_character(caster)
    ui._set_targets([target])
    ui._apply_custom_effect(replace(effect, **changes))


def _hit(ui, attacker, target, damage="5 slashing"):
    """attacker's attack roll and damage typed in the main window."""
    ui._select_character(attacker)
    ui._set_targets([target])
    ui.attack_roll_input.setText("30")
    ui.damage_input.setText(damage)
    ui._apply_damage_checked()


def _invisible_tiger(ui, pirate, tiger):
    _cast(ui, pirate, tiger, "Invisibility")
    assert {"Invisible", "Invisibility"} <= set(tiger["conditions"])


def test_invisibility_ends_after_its_bearer_makes_an_attack_roll(fight):
    ui, pirate, tiger = fight
    _invisible_tiger(ui, pirate, tiger)
    _hit(ui, tiger, pirate)
    assert not {"Invisible", "Invisibility"} & set(tiger["conditions"])
    assert "Tiger's Invisibility ends: it makes an attack roll" in _lines(ui)


def test_invisibility_ends_as_its_bearer_deals_damage(fight):
    """Damage with no attack roll: a save effect's."""
    ui, pirate, tiger = fight
    _invisible_tiger(ui, pirate, tiger)
    ui._select_character(tiger)
    ui._set_targets([pirate])
    ui._apply_custom_effect(CustomEffect(name="Roar", damage=[(4, "Thunder")]))
    assert "Invisibility" not in tiger["conditions"]
    assert "Tiger's Invisibility ends: it deals damage" in _lines(ui)


def test_invisibility_ends_as_its_bearer_casts_a_spell(fight):
    ui, pirate, tiger = fight
    _invisible_tiger(ui, pirate, tiger)
    _cast(ui, tiger, pirate, "Shield of Faith")
    assert "Invisibility" not in tiger["conditions"]
    assert "Tiger's Invisibility ends: it casts a spell" in _lines(ui)


def test_casting_invisibility_on_oneself_keeps_it(fight):
    ui, pirate, _ = fight
    _cast(ui, pirate, pirate, "Invisibility")
    assert {"Invisible", "Invisibility"} <= set(pirate["conditions"])


def test_sleep_ends_as_its_target_takes_damage(fight):
    ui, pirate, tiger = fight
    _cast(ui, pirate, tiger, "Sleep", typed_totals={id(tiger): 1})
    assert {"Incapacitated", "Sleep"} <= set(tiger["conditions"])
    _hit(ui, pirate, tiger)
    assert not {"Incapacitated", "Sleep"} & set(tiger["conditions"])
    assert "Tiger's Sleep ends: it takes damage" in _lines(ui)


def test_armor_of_agathys_ends_only_when_no_temporary_hit_points_are_left(fight):
    ui, pirate, tiger = fight
    _cast(ui, pirate, pirate, "Armor of Agathys")
    assert "Armor of Agathys" in pirate["conditions"]
    temp = pirate["temp_hp"]
    _hit(ui, tiger, pirate, f"{temp - 1} slashing")
    assert "Armor of Agathys" in pirate["conditions"]
    _hit(ui, tiger, pirate, "3 slashing")
    assert pirate["temp_hp"] == 0
    assert "Armor of Agathys" not in pirate["conditions"]


def test_turn_undead_and_its_conditions_end_as_it_takes_damage(fight):
    ui, pirate, tiger = fight
    for name in ("Frightened", "Incapacitated", "Turn Undead"):
        tiger["conditions"].append(name)
    give_modifiers(tiger, "Turn Undead", (EndsWhen((EndEvent.TAKES_DAMAGE,)),))
    _hit(ui, pirate, tiger)
    assert "Turn Undead" not in tiger["conditions"]
    assert "Tiger's Turn Undead ends: it takes damage" in _lines(ui)


def test_elemental_attunement_ends_as_its_bearer_is_incapacitated(fight):
    ui, pirate, tiger = fight
    tiger["conditions"].append("Elemental Attunement")
    give_modifiers(
        tiger, "Elemental Attunement", (EndsWhen((EndEvent.INCAPACITATED,)),)
    )
    ui._select_character(pirate)
    ui._set_targets([tiger])
    ui._apply_custom_effect(CustomEffect(name="Stun", condition="Stunned"))
    assert "Elemental Attunement" not in tiger["conditions"]
    assert (
        "Tiger's Elemental Attunement ends: it has the Incapacitated condition"
        in _lines(ui)
    )


def test_a_badge_without_ends_when_stays(fight):
    ui, pirate, tiger = fight
    tiger["conditions"].append("Bless")
    _hit(ui, pirate, tiger)
    assert "Bless" in tiger["conditions"]
