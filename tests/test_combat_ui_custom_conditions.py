"""The combat UI's Custom Condition (ConditionsMixin._add_custom_condition and
its dialog): any condition typed in goes on every target, with an optional
note and a duration that ends it by itself at the right turn boundary."""

import pytest
from PyQt6.QtWidgets import QComboBox, QDialog, QLabel, QLineEdit, QMessageBox
from PyQt6.QtWidgets import QPushButton, QSpinBox

from Combat.Combatants import Pirate, Tiger
from tests._combat_ui import make_ui, open_dialog

UNTIL_START_OF_SOURCE = {"until": "start", "of": "source"}
UNTIL_END_OF_SOURCE = {"until": "end", "of": "source"}
UNTIL_START_OF_TARGET = {"until": "start", "of": "target"}
UNTIL_END_OF_TARGET = {"until": "end", "of": "target"}


@pytest.fixture
def fight(tmp_path):
    """A Pirate (initiative 15) and a Tiger (10) in round 1, the Pirate's
    turn, the Pirate the source and the Tiger the target."""
    ui = make_ui(tmp_path, [Pirate(), Tiger()])
    pirate, tiger = ui.characters
    ui._initiative_inputs[id(pirate)].setText("15")
    ui._initiative_inputs[id(tiger)].setText("10")
    ui._start_combat()
    ui._select_character(pirate)
    ui._select_target_character(tiger)
    return ui, pirate, tiger


def _turns(ui, count: int):
    for _ in range(count):
        ui._advance_turn()


def _whose_turn(ui) -> tuple[int, str]:
    return ui.round_number, ui.initiative_order[ui.current_turn_idx]["name"]


def test_untimed_condition_stays_until_removed(fight):
    ui, _, tiger = fight
    ui._add_custom_condition("Hexed", None, "Extra 1d6 necrotic from the Pirate")

    _turns(ui, 10)

    assert "Hexed" in tiger["conditions"]
    assert tiger.get("timed_conditions") == []
    description, _ = ui._condition_description_and_color(tiger, "Hexed")
    assert description == "Extra 1d6 necrotic from the Pirate"


def test_until_start_of_source_next_turn(fight):
    ui, _, tiger = fight
    ui._add_custom_condition("Dodging the Pirate", UNTIL_START_OF_SOURCE)

    _turns(ui, 1)  # the Tiger's turn
    assert "Dodging the Pirate" in tiger["conditions"]
    _turns(ui, 1)  # round 2, the Pirate's turn starts
    assert _whose_turn(ui) == (2, "Pirate")
    assert "Dodging the Pirate" not in tiger["conditions"]
    assert tiger["timed_conditions"] == []


def test_until_end_of_source_next_turn_given_on_its_own_turn(fight):
    """Given on the Pirate's turn, its *next* turn is round 2's."""
    ui, _, tiger = fight
    ui._add_custom_condition("Vexed", UNTIL_END_OF_SOURCE)

    _turns(ui, 2)  # round 1 Pirate turn ended, round 2 Pirate turn started
    assert "Vexed" in tiger["conditions"]
    _turns(ui, 1)  # round 2 Pirate turn ends
    assert _whose_turn(ui) == (2, "Tiger")
    assert "Vexed" not in tiger["conditions"]


def test_until_end_of_target_next_turn(fight):
    ui, _, tiger = fight
    ui._add_custom_condition("Sapped", UNTIL_END_OF_TARGET)

    _turns(ui, 1)  # the Tiger's turn starts
    assert "Sapped" in tiger["conditions"]
    _turns(ui, 1)  # ... and ends
    assert "Sapped" not in tiger["conditions"]


def test_target_durations_follow_each_target_own_turn(fight):
    """Two targets: each one's condition ends at its own next turn."""
    ui, pirate, tiger = fight
    ui._select_target_character(pirate, ctrl=True)
    assert ui.target_characters == [tiger, pirate]
    ui._add_custom_condition("Shaken", UNTIL_START_OF_TARGET)

    _turns(ui, 1)  # the Tiger's turn starts
    assert "Shaken" not in tiger["conditions"]
    assert "Shaken" in pirate["conditions"]
    _turns(ui, 1)  # the Pirate's turn starts
    assert "Shaken" not in pirate["conditions"]


def test_one_round_lasts_until_the_same_turn_next_round(fight):
    ui, _, tiger = fight
    _turns(ui, 1)  # given on the Tiger's turn
    ui._add_custom_condition("Off Balance", {"seconds": 6})

    _turns(ui, 1)  # round 2, the Pirate's turn
    assert "Off Balance" in tiger["conditions"]
    _turns(ui, 1)  # round 2, the Tiger's turn
    assert "Off Balance" not in tiger["conditions"]


def test_one_minute_lasts_ten_rounds(fight):
    ui, _, tiger = fight
    ui._add_custom_condition("Blessed", {"seconds": 60})

    _turns(ui, 19)  # round 10, the Tiger's turn
    assert _whose_turn(ui) == (10, "Tiger")
    assert "Blessed" in tiger["conditions"]
    assert tiger["timed_conditions"][0]["time_left"] == 6
    _turns(ui, 1)  # round 11, the Pirate's turn
    assert "Blessed" not in tiger["conditions"]


def test_giving_it_again_replaces_its_duration(fight):
    ui, _, tiger = fight
    ui._add_custom_condition("Marked", {"seconds": 6})
    ui._add_custom_condition("Marked", {"seconds": 60})

    assert tiger["conditions"].count("Marked") == 1
    assert [e["time_left"] for e in tiger["timed_conditions"]] == [60]

    ui._add_custom_condition("Marked", None)
    assert tiger["timed_conditions"] == []


def test_removing_the_condition_drops_its_timer(fight):
    ui, _, tiger = fight
    ui._add_custom_condition("Marked", {"seconds": 60}, "a note")

    ui._remove_condition_from(tiger, "Marked")

    assert tiger["timed_conditions"] == []
    assert "Marked" not in tiger.get("custom_condition_descriptions", {})


def test_undo_takes_it_back(fight):
    ui, _, tiger = fight
    ui._add_custom_condition("Marked", {"seconds": 60}, "a note")

    ui._undo_last()

    assert "Marked" not in tiger["conditions"]
    assert "timed_conditions" not in tiger


def test_card_shows_timed_conditions(fight):
    ui, _, tiger = fight
    ui._add_custom_condition("Vexed", UNTIL_END_OF_SOURCE)

    texts = [lbl.text() for lbl in ui._card_widgets[id(tiger)].findChildren(QLabel)]
    assert "Timed Conditions:" in texts
    assert "Until the end of Pirate's next turn" in texts


def test_dialog_applies_a_custom_duration(fight, monkeypatch):
    ui, _, tiger = fight
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    name_combo, duration_combo, unit_combo = dlg.findChildren(QComboBox)
    name_combo.setCurrentText("Restrained by vines")
    # The notes box; the combo and spin boxes hold line edits of their own.
    (notes,) = [e for e in dlg.findChildren(QLineEdit) if e.parent() is dlg]
    notes.setText("DC 13 Str save ends")
    duration_combo.setCurrentIndex(duration_combo.findData("custom"))
    dlg.findChild(QSpinBox).setValue(3)
    unit_combo.setCurrentText("rounds")
    apply_btn = next(b for b in dlg.findChildren(QPushButton) if b.text() == "Apply")
    apply_btn.click()

    assert "Restrained by vines" in tiger["conditions"]
    assert tiger["timed_conditions"][0]["time_left"] == 18
    assert tiger["custom_condition_descriptions"] == {
        "Restrained by vines": "DC 13 Str save ends"
    }


def test_dialog_names_the_source_in_its_durations(fight, monkeypatch):
    ui, _, _ = fight
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    duration_combo = dlg.findChildren(QComboBox)[1]
    labels = [duration_combo.itemText(i) for i in range(duration_combo.count())]
    assert "Until the start of Pirate's next turn" in labels
    assert labels[-1] == "Custom..."


def test_dialog_needs_a_target(fight, monkeypatch):
    ui, _, _ = fight
    ui.target_characters = []
    warnings = []
    monkeypatch.setattr(QMessageBox, "warning", lambda *a: warnings.append(a))
    monkeypatch.setattr(QDialog, "exec", lambda self: pytest.fail("opened"))

    ui._show_custom_condition_dialog()

    assert len(warnings) == 1
