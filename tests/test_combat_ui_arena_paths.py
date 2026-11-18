"""The way a walk goes, in the combat UI (Notes/combat-arena-plan.md, step
23): an Opportunity Attack for a walk that passes through an enemy's reach,
Polearm Master's Reactive Strike for one that enters its reach, Undo taking
a walk's buttons back, and an attacker's other buttons going once it spends
its Reaction."""

import pytest

from Builds.Characters.Y2024_Paladin_Devotion_Edmund import (
    Y2024PaladinDevotionEdmundCharacterBuilder as Edmund,
)
from CharacterContent.Features.CharacterFeats.GeneralFeats import PolearmMaster
from CharacterContent.Items.Weapons.SimpleMelee import Spear
from Combat.Arena.arena import POSITION_KEY
from Combat.Arena.geometry import Cell
from Combat.Effects.triggers import OpportunityAttack
from Combat.Monsters.CR_1.monsters import Tiger
from Core.Definitions import Ability
from tests._combat_ui import make_ui


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    from PyQt6.QtWidgets import QMessageBox

    def refuse(*args, **kwargs):
        raise AssertionError(f"Unexpected question: {args[1:3]}")

    monkeypatch.setattr(QMessageBox, "question", refuse)


def _fight(tmp_path):
    """Edmund (initiative 15) at F4, two cells above the Large Tiger (10) at
    G6-H7; Edmund's turn, the map in use."""
    ui = make_ui(tmp_path, [Tiger()], [Edmund().build()])
    player, tiger = ui.characters
    ui._initiative_inputs[id(player)].setText("15")
    ui._initiative_inputs[id(tiger)].setText("10")
    ui._start_combat()
    player[POSITION_KEY] = [5, 3]
    tiger[POSITION_KEY] = [6, 5]
    ui.arena_settings.in_use = True
    return ui, player, tiger


def _prompts(ui) -> list[OpportunityAttack]:
    return [p for p in ui._hit_prompts if isinstance(p, OpportunityAttack)]


def _buttons(ui) -> list[str]:
    layout = ui._turn_prompts_layout
    return [
        layout.itemAt(i).widget().text()
        for i in range(layout.count())
        if layout.itemAt(i).widget() is not None
        and not layout.itemAt(i).widget().isHidden()
    ]


def test_walking_past_the_tiger_offers_its_opportunity_attack(tmp_path):
    """F4 to F9: 15 ft. from the Tiger at both ends, beside it on the way."""
    ui, player, tiger = _fight(tmp_path)
    ui._move_combatant(player, Cell(5, 8))
    [prompt] = _prompts(ui)
    assert prompt.attacker is tiger and prompt.name == "Opportunity Attack"
    assert "Tiger: Opportunity Attack on Edmund (Reaction)" in _buttons(ui)
    assert "leaves Tiger's reach" in ui._status_label.text()


def test_undoing_the_walk_takes_its_button_back(tmp_path):
    ui, player, tiger = _fight(tmp_path)
    ui._move_combatant(player, Cell(5, 8))
    ui._undo_last()
    assert _prompts(ui) == []
    assert not any("Opportunity Attack" in b for b in _buttons(ui))
    assert player[POSITION_KEY] == [5, 3]


def test_spending_the_reaction_takes_the_attackers_buttons_away(tmp_path):
    ui, player, tiger = _fight(tmp_path)
    ui._move_combatant(player, Cell(5, 8))
    assert _prompts(ui)
    ui._add_action_use("Reaction", tiger, ask=False)
    assert _prompts(ui) == []
    assert not any("Opportunity Attack" in b for b in _buttons(ui))


def test_entering_a_polearm_masters_reach_offers_its_reactive_strike(tmp_path):
    """The Tiger walks up to Edmund, who holds a Spear and has Polearm
    Master, on its own turn."""
    ui, player, tiger = _fight(tmp_path)
    player[POSITION_KEY] = [3, 5]
    tiger[POSITION_KEY] = [9, 5]
    player["_feature_objects"] = [
        *player["_feature_objects"],
        PolearmMaster(4, Ability.STRENGTH),
    ]
    player["_weapons_objects"] = [*player["_weapons_objects"], Spear()]
    ui._advance_turn()
    assert ui._current_turn_character() is tiger
    ui._move_combatant(tiger, Cell(4, 5))
    [prompt] = _prompts(ui)
    assert prompt.attacker is player and prompt.target is tiger
    assert prompt.name == "Reactive Strike"
    assert "Edmund: Reactive Strike on Tiger (Reaction)" in _buttons(ui)
    assert "enters Edmund's reach: Reactive Strike" in ui._status_label.text()
