"""The Custom Effect dialog with what Phase 2 of Notes/combat-effects-plan.md
added: several conditions from one effect (Turn Undead, Tasha's Hideous
Laughter), an effect repeated several times in one Apply (Scorching Ray's
rays), spells with a row per way to cast them (Command, Ice Knife), and a
feature's extension used as one more option of it (Radiance of the Dawn, a
use of Channel Divinity).

Expected values come from the rules text: Turn Undead gives Frightened and
Incapacitated, Tasha's ends both of its conditions on one successful save,
Scorching Ray at level 2 is three ranged spell attacks for 2d6 Fire each,
and Ice Knife's explosion is part of the same casting.
"""

import random

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox, QPushButton, QSpinBox, QTreeWidget

from Builds.Characters.Y2024_Cleric_Light_GabrielGreybeard import (
    Y2024ClericLightGabrielGreybeardCharacterBuilder as Gabriel,
)
from Builds.Characters.Y2024_Paladin_Devotion_Edmund import (
    Y2024PaladinDevotionEdmundCharacterBuilder as Edmund,
)
from Combat.Combatants import Tiger
from Combat.CombatUIQt.saves import CustomEffect
from tests._combat_ui import make_ui, open_dialog


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    """Nothing here should ask: an out-of-resources question fails the test."""
    from PyQt6.QtWidgets import QMessageBox

    def refuse(*args, **kwargs):
        raise AssertionError(f"Unexpected question: {args[1:3]}")

    monkeypatch.setattr(QMessageBox, "question", refuse)


def _fight(tmp_path, builder):
    """The player against a Tiger, the player's turn, targeting the Tiger."""
    ui = make_ui(tmp_path, [Tiger()], [builder().build()])
    player, tiger = ui.characters
    ui._initiative_inputs[id(player)].setText("15")
    ui._initiative_inputs[id(tiger)].setText("10")
    ui._start_combat()
    ui._select_character(player)
    ui._select_target_character(tiger)
    return ui, player, tiger


@pytest.fixture
def edmund(tmp_path):
    return _fight(tmp_path, Edmund)


@pytest.fixture
def gabriel(tmp_path):
    return _fight(tmp_path, Gabriel)


def _rolls(monkeypatch, value: int):
    monkeypatch.setattr(random, "randint", lambda low, high: value)


def _pick(dlg, name: str):
    tree = dlg.findChild(QTreeWidget, "effectOptions")
    rows = [
        tree.topLevelItem(i).child(j)
        for i in range(tree.topLevelItemCount())
        for j in range(tree.topLevelItem(i).childCount())
    ]
    row = next(r for r in rows if r.data(0, Qt.ItemDataRole.UserRole).name == name)
    tree.setCurrentItem(row)


def _apply(dlg):
    next(b for b in dlg.findChildren(QPushButton) if b.text() == "Apply").click()


def _log(ui) -> list[str]:
    return [event["text"] for event in ui._read_log()["round_1"]]


# ---------------------------------------------------------------------------
# Several conditions


def test_turn_undead_gives_both_conditions_and_spends_channel_divinity(
    gabriel, monkeypatch
):
    ui, cleric, tiger = gabriel
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Turn Undead")
    name_box = dlg.findChild(QComboBox, "conditionName")
    assert name_box.currentText() == "Frightened + Incapacitated"
    _rolls(monkeypatch, 1)  # the Tiger fails its Wisdom save
    _apply(dlg)
    assert {"Frightened", "Incapacitated"} <= set(tiger["conditions"])
    assert cleric["feature_uses_used"] == {"Channel Divinity": 1}


def test_one_repeat_save_ends_every_condition_the_effect_gave(edmund, monkeypatch):
    """Tasha's: a successful save at the end of its turn ends the spell, so
    both Prone and Incapacitated."""
    ui, _, tiger = edmund
    _rolls(monkeypatch, 1)
    ui._apply_custom_effect(
        CustomEffect(
            name="Tasha's Hideous Laughter",
            condition="Incapacitated + Prone",
            ability="WIS",
            dc=30,
            repeat_save=True,
        )
    )
    assert {"Incapacitated", "Prone"} <= set(tiger["conditions"])
    (entry,) = tiger["repeat_saves"]
    assert (entry["condition"], entry["also"]) == ("Incapacitated", ["Prone"])
    _rolls(monkeypatch, 20)
    entry["dc"] = 5
    ui._roll_repeat_save(tiger, entry, "Wisdom")
    assert not {"Incapacitated", "Prone"} & set(tiger["conditions"])
    assert any("ends Incapacitated and Prone" in text for text in _log(ui))


# ---------------------------------------------------------------------------
# Times


def test_scorching_ray_is_three_attacks_for_one_slot_and_one_undo(edmund, monkeypatch):
    ui, paladin, tiger = edmund
    paladin["spell_slots"] = {2: 1}
    tiger["ac"] = 10
    tiger["hp"] = tiger["max_hp"] = 500  # alive for all three rays
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Scorching Ray")
    times = dlg.findChild(QSpinBox, "effectTimes")
    assert times.value() == 3
    _rolls(monkeypatch, 10)  # each d20 a 10: with +4, each ray hits AC 10
    hp = tiger["hp"]
    _apply(dlg)
    lines = [line for turn in ui._public_log()[0]["turns"] for line in turn["lines"]]
    assert sum(line["kind"] == "hit" for line in lines) == 3  # three attack rolls
    assert any("Scorching Ray (3 of 3)" in text for text in _log(ui))
    assert paladin["spell_slots"] == {2: 0}  # one slot for all three
    assert sum(1 for text in _log(ui) if "casts Scorching Ray" in text) == 1
    assert tiger["hp"] < hp
    ui._undo_last()
    assert tiger["hp"] == hp
    assert paladin["spell_slots"] == {2: 1}
    assert ui.history == []


def test_a_higher_slot_adds_a_ray(edmund, monkeypatch):
    ui, paladin, _ = edmund
    paladin["spell_slots"] = {2: 1, 3: 1}
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Scorching Ray")
    slots = dlg.findChild(QComboBox, "spellSlot")
    slots.setCurrentIndex(slots.findData(3))
    assert dlg.findChild(QSpinBox, "effectTimes").value() == 4


# ---------------------------------------------------------------------------
# A row per way to cast a spell


def test_a_commands_option_spends_a_casting_of_command(edmund, monkeypatch):
    ui, paladin, tiger = edmund
    paladin["spell_slots"] = {1: 2}
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Command: Grovel")
    _rolls(monkeypatch, 1)
    _apply(dlg)
    assert "Prone" in tiger["conditions"]
    assert paladin["spell_slots"] == {1: 1}
    assert any("casts Command" in text for text in _log(ui))


def test_ice_knifes_explosion_spends_no_slot(edmund, monkeypatch):
    ui, paladin, tiger = edmund
    paladin["spell_slots"] = {1: 2}
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Ice Knife: explosion")
    assert dlg.findChild(QComboBox, "spellSlot").currentData() is None
    _rolls(monkeypatch, 1)
    hp = tiger["hp"]
    _apply(dlg)
    assert tiger["hp"] < hp
    assert paladin["spell_slots"] == {1: 2}
    assert not any("casts Ice Knife" in text for text in _log(ui))


# ---------------------------------------------------------------------------
# An extension's own option


def test_radiance_of_the_dawn_spends_a_use_of_channel_divinity(gabriel, monkeypatch):
    ui, cleric, tiger = gabriel
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Radiance of the Dawn")
    _rolls(monkeypatch, 1)
    hp = tiger["hp"]
    _apply(dlg)
    assert tiger["hp"] < hp
    assert cleric["feature_uses_used"] == {"Channel Divinity": 1}
