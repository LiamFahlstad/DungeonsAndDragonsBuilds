"""Later steps of a casting (Notes/combat-effects-plan.md, step 9.7): rows a
spell is used again with on a later turn, which spend no slot, and whose
badges the caster's concentration on the spell holds.

Expected values are the rules text's:

- Hunter's Mark: "If the target drops to 0 Hit Points before the spell
  ends, you can take a Bonus Action on a later turn to move the mark to a
  new creature you can see within range."
- Hex: "you deal an extra 1d6 Necrotic damage to the target whenever you hit
  it with an attack roll ... If the target drops to 0 Hit Points before this
  spell ends, you can take a Bonus Action on a later turn to curse a new
  creature."
- Witch Bolt: "On each of your later turns, you can take a Bonus Action to
  deal 1d12 Lightning damage to the target automatically, even if the first
  attack missed."
"""

import pytest
from PyQt6.QtWidgets import QDialog, QMessageBox

from CharacterContent.Spells.SpellFactory import SpellFactory
from Combat.Combatants import Pirate, Tiger
from Combat.Definitions import ActionCost
from Combat.Effects.active_effects import find_effect
from Combat.Fight.effect_options import spell_options
from Combat.Fight.picked import picked_effect
from Core.Definitions import DamageType
from Model.Content.CombatModifiers import ExtraDamageFrom
from tests._combat_ui import make_ui


def _rows(spell: str) -> dict:
    return {o.name: o for o in spell_options(SpellFactory.create(spell), None)}


@pytest.mark.parametrize(
    "spell, row",
    [
        ("Hunter's Mark", "Hunter's Mark: move the mark"),
        ("Hex", "Hex: move the curse"),
        ("Witch Bolt", "Witch Bolt: later turn"),
    ],
)
def test_a_later_step_is_a_bonus_action_and_spends_no_slot(spell, row):
    later = _rows(spell)[row]
    assert later.action_cost == ActionCost.BONUS_ACTION
    assert not later.counts_uses and later.slot_level is None


def test_the_moved_mark_and_curse_give_the_casts_badge():
    for spell, row, badge in (
        ("Hunter's Mark", "Hunter's Mark: move the mark", "Hunter's Mark"),
        ("Hex", "Hex: move the curse", "Hex"),
    ):
        rows = _rows(spell)
        cast, moved = rows[spell], rows[row]
        assert cast.badge_modifiers == moved.badge_modifiers
        ((name, _),) = moved.badge_modifiers
        assert name == badge


def test_hex_deals_1d6_necrotic_on_its_casters_hits():
    ((_, modifiers),) = _rows("Hex")["Hex"].badge_modifiers
    assert ExtraDamageFrom("1d6", DamageType.NECROTIC) in modifiers


def test_witch_bolts_later_damage_needs_no_roll():
    later = _rows("Witch Bolt")["Witch Bolt: later turn"]
    assert later.damage_at(None) == "1d12 Lightning"
    assert later.roll != "Attack roll"


# ---------------------------------------------------------------------------
# In the window


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)
    monkeypatch.setattr(QMessageBox, "question", refuse)


def _apply(ui, caster, target, row):
    effect = picked_effect(row, {})
    assert effect is not None
    ui._select_character(caster)
    ui._set_targets([target])
    ui._apply_custom_effect(effect)


def test_a_moved_mark_is_held_by_the_same_concentration(tmp_path):
    ui = make_ui(tmp_path, [Pirate(), Tiger(), Tiger()])
    pirate, first, second = ui.characters
    second["name"] = "Tiger 2"  # records go by name, as numbered summons do
    for char, value in zip(ui.characters, (20, 10, 5)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    rows = {
        o.name: o for o in spell_options(SpellFactory.create("Hunter's Mark"), pirate)
    }
    _apply(ui, pirate, first, rows["Hunter's Mark"])
    assert "Concentrating" in pirate["conditions"]
    assert "Hunter's Mark" in first["conditions"]
    # The first one drops; on a later turn (the Pirate's next), the mark moves.
    for _ in range(3):
        ui._advance_turn()
    _apply(ui, pirate, second, rows["Hunter's Mark: move the mark"])
    record = find_effect(second, "Hunter's Mark")
    assert record is not None and record["concentration"] == pirate["name"]
    (entry,) = [e for e in pirate["active_spells"] if e["name"] == "Hunter's Mark"]
    assert {row["target"] for row in entry["applied"]} == {
        first["name"],
        second["name"],
    }
    # Its concentration ends: both marks go.
    ui._remove_condition_from(pirate, "Concentrating", source=pirate)
    assert "Hunter's Mark" not in first["conditions"]
    assert "Hunter's Mark" not in second["conditions"]
