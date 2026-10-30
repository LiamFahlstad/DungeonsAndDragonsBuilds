"""The combat UI's Previous button (TurnsMixin._previous_turn): going back a
turn after pressing Next by mistake. Straight after Next it undoes that press
completely; after anything else it only moves the turn back."""

import pytest
from PyQt6.QtWidgets import QDialog, QMessageBox

from Combat.Combatants import Pirate, Tiger
from Combat.CombatUIQt.undo import _combat_data
from tests._combat_ui import make_ui


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    """A modal dialog would block the test forever; fail it instead."""

    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)


@pytest.fixture
def fight(tmp_path):
    """A Pirate (initiative 15) and a Tiger (10) in round 1, the Pirate's
    turn."""
    ui = make_ui(tmp_path, [Pirate(), Tiger()])
    pirate, tiger = ui.characters
    ui._initiative_inputs[id(pirate)].setText("15")
    ui._initiative_inputs[id(tiger)].setText("10")
    ui._start_combat()
    ui._select_character(pirate)
    ui._select_target_character(tiger)
    return ui, pirate, tiger


def _everything(ui) -> dict:
    return {
        "combatants": [_combat_data(c) for c in ui.characters],
        "turn": ui.current_turn_idx,
        "round": ui.round_number,
        "round_label": ui.round_label.text(),
        "log": {k: v for k, v in ui._read_log().items() if k.split("_")[-1].isdigit()},
    }


def _damage(ui, amount: int):
    ui.damage_type_combo.setCurrentIndex(1)  # reset to "none" after every hit
    ui.damage_input.setText(str(amount))
    ui._apply_damage()


def test_nothing_before_the_first_turn(fight):
    ui, _, _ = fight
    assert not ui._prev_turn_btn.isEnabled()
    before = _everything(ui)

    ui._previous_turn()

    assert _everything(ui) == before
    assert ui.history == []


def test_previous_right_after_next_undoes_it(fight):
    ui, pirate, _ = fight
    pirate["active_spells"] = [
        {"name": "Bless", "time_left": 6, "duration": 60, "concentration": False}
    ]
    ui._advance_turn()  # Tiger's turn
    ui._add_action_use("Action")
    before = _everything(ui)
    ui._advance_turn()  # Round 2: Bless runs out, the Pirate's tallies reset
    assert ui.round_number == 2 and pirate["active_spells"] == []
    assert ui._prev_turn_btn.isEnabled()

    ui._previous_turn()

    assert _everything(ui) == before
    assert ui._next_turn_btn.text() == "Next Round"


def test_several_extra_presses_go_back_one_each(fight):
    ui, _, _ = fight
    start = _everything(ui)
    for _ in range(3):
        ui._advance_turn()
    assert (ui.round_number, ui.current_turn_idx) == (2, 1)

    ui._previous_turn()
    assert (ui.round_number, ui.current_turn_idx) == (2, 0)
    ui._previous_turn()
    ui._previous_turn()

    assert _everything(ui) == start
    assert not ui._prev_turn_btn.isEnabled()


def test_previous_after_something_else_only_moves_the_turn(fight):
    ui, _, tiger = fight
    ui._advance_turn()
    ui._advance_turn()  # Round 2, the Pirate's turn
    _damage(ui, 5)
    hp = tiger["hp"]

    ui._previous_turn()

    assert (ui.round_number, ui.current_turn_idx) == (1, 1)
    assert ui.round_label.text() == "Round 1"
    assert tiger["hp"] == hp
    assert ui.selected_character is tiger  # the source follows the turn

    ui._undo_last()  # the step back is itself one undo
    assert (ui.round_number, ui.current_turn_idx) == (2, 0)
    assert tiger["hp"] == hp
