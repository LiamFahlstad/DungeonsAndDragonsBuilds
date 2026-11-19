"""Opportunity Attacks in the combat UI (Rules Glossary, Opportunity Attacks):
a walk on the mover's own turn that leaves an enemy's reach puts a
turn-column button for each enemy that can still react, which opens Use /
Cast with that enemy as the source, the mover as the target, one melee
attack picked and the Reaction as its cost, whatever row the GM picks."""

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox, QPushButton, QTreeWidget

from Builds.Characters.Y2024_Paladin_Devotion_Edmund import (
    Y2024PaladinDevotionEdmundCharacterBuilder as Edmund,
)
from Combat.Arena.arena import POSITION_KEY
from Combat.Arena.geometry import Cell
from Combat.Monsters.CR_1.monsters import Tiger
from Combat.CombatUIQt.effect_options import opportunity_attack_row
from Combat.Effects.triggers import OpportunityAttack
from Combat.PlayerCombatant import combatant_from_character
from Model.Content.StandardActions import DISENGAGE
from tests._combat_ui import make_ui, open_dialog
from tests._combat_ui import described


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    """Nothing here should ask: an out-of-resources question fails the test."""
    from PyQt6.QtWidgets import QMessageBox

    def refuse(*args, **kwargs):
        raise AssertionError(f"Unexpected question: {args[1:3]}")

    monkeypatch.setattr(QMessageBox, "question", refuse)


def _fight(tmp_path):
    """Edmund (initiative 15) next to a Tiger (10) on the map, Edmund's turn."""
    ui = make_ui(tmp_path, [Tiger()], [Edmund().build()])
    player, tiger = ui.characters
    ui._initiative_inputs[id(player)].setText("15")
    ui._initiative_inputs[id(tiger)].setText("10")
    ui._start_combat()
    player[POSITION_KEY] = [5, 5]
    tiger[POSITION_KEY] = [6, 5]
    return ui, player, tiger


def _prompt_buttons(ui) -> list[QPushButton]:
    return [
        b
        for b in ui._turn_prompts_box.findChildren(QPushButton, "turnPromptBtn")
        if not b.isHidden()
    ]


def _opportunity_prompts(ui) -> list[OpportunityAttack]:
    return [p for p in ui._hit_prompts if isinstance(p, OpportunityAttack)]


def test_walking_out_of_reach_puts_a_button_for_the_opportunity_attack(tmp_path):
    ui, player, tiger = _fight(tmp_path)
    ui._move_combatant(player, Cell(2, 5))
    [prompt] = _opportunity_prompts(ui)
    assert prompt.attacker is tiger and prompt.target is player
    assert [b.text() for b in _prompt_buttons(ui)] == [
        "Tiger: Opportunity Attack on Edmund (Reaction)"
    ]


def test_the_button_opens_use_cast_with_a_melee_attack_costing_the_reaction(
    tmp_path, monkeypatch
):
    ui, player, tiger = _fight(tmp_path)
    ui._move_combatant(player, Cell(2, 5))
    [button] = _prompt_buttons(ui)
    dlg = open_dialog(monkeypatch, button.click)
    assert ui.selected_character is tiger
    assert ui.target_characters == [player]
    tree = dlg.findChild(QTreeWidget, "effectOptions")
    picked = tree.currentItem().data(0, Qt.ItemDataRole.UserRole)
    assert picked.name == opportunity_attack_row(tiger) != ""
    assert dlg.findChild(QComboBox, "actionCost").currentData() == "Reaction"
    # The button goes once used.
    assert _opportunity_prompts(ui) == []
    next(b for b in dlg.findChildren(QPushButton) if b.text() == "Apply").click()
    assert tiger["action_uses"].get("Reaction") == 1
    assert not tiger["action_uses"].get("Action")


def test_the_reaction_stays_the_cost_when_the_gm_picks_another_row(
    tmp_path, monkeypatch
):
    ui, player, tiger = _fight(tmp_path)
    ui._move_combatant(player, Cell(2, 5))
    [button] = _prompt_buttons(ui)
    dlg = open_dialog(monkeypatch, button.click)
    tree = dlg.findChild(QTreeWidget, "effectOptions")
    rows = [
        tree.topLevelItem(i).child(j)
        for i in range(tree.topLevelItemCount())
        for j in range(tree.topLevelItem(i).childCount())
    ]
    other = next(
        r
        for r in rows
        if r.data(0, Qt.ItemDataRole.UserRole).name == "Dash"  # costs an Action
    )
    tree.setCurrentItem(other)
    assert dlg.findChild(QComboBox, "actionCost").currentData() == "Reaction"


def test_no_button_when_disengaged_or_the_reaction_is_used(tmp_path):
    ui, player, tiger = _fight(tmp_path)
    player["conditions"].append(DISENGAGE)
    ui._move_combatant(player, Cell(2, 5))
    assert _opportunity_prompts(ui) == []
    ui, player, tiger = _fight(tmp_path / "again")
    tiger["action_uses"] = {"Reaction": 1}
    ui._move_combatant(player, Cell(2, 5))
    assert _opportunity_prompts(ui) == []


def test_walking_out_twice_keeps_one_button(tmp_path):
    ui, player, tiger = _fight(tmp_path)
    ui._move_combatant(player, Cell(2, 5))
    ui._move_combatant(player, Cell(5, 5))
    ui._move_combatant(player, Cell(2, 5))
    assert len(_opportunity_prompts(ui)) == 1


def test_the_buttons_go_as_the_next_turn_starts(tmp_path):
    ui, player, tiger = _fight(tmp_path)
    ui._move_combatant(player, Cell(2, 5))
    ui._advance_turn()
    assert _opportunity_prompts(ui) == []


def test_the_attack_picked_is_a_melee_one():
    edmund = combatant_from_character(Edmund().build())
    weapons = edmund["_weapons_objects"]
    melee = [w.name for w in weapons if w.traits.is_melee and not w.is_unarmed_strike]
    assert opportunity_attack_row(edmund) == melee[0]
    archer = {
        "name": "Archer",
        "actions": [
            described(
                {
                    "name": "Longbow",
                    "description": "Ranged Attack Roll: +5, range 150/600 ft. Hit:"
                    " 7 (1d8 + 3) Piercing damage.",
                }
            ),
            described(
                {
                    "name": "Dagger",
                    "description": "Melee or Ranged Attack Roll: +5, reach 5 ft. or"
                    " range 20/60 ft. Hit: 5 (1d4 + 3) Piercing damage.",
                }
            ),
        ],
    }
    # No plain melee attack: one that can be melee or ranged, never the bow.
    assert opportunity_attack_row(archer) == "Dagger"
    archer["actions"].pop()
    assert opportunity_attack_row(archer) == ""
