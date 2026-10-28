"""Undo in the combat UI (undo.py, LoggingMixin._undo_last): one undo takes
back exactly one operation - all of the combat state it changed, and
exactly the lines it wrote to the encounter log (which the party's state
is replayed from on the next run)."""

import pytest
from PyQt6.QtWidgets import QDialog, QMessageBox

from CharacterContent.Spells.SpellFactory import SpellFactory
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
    pirate["spell_slots"] = {1: 2}
    ui._select_character(pirate)
    ui._select_target_character(tiger)
    return ui, pirate, tiger


def _rounds(log: dict) -> dict:
    """The round_<n> lists of a log (not its round_number)."""
    return {k: v for k, v in log.items() if k.split("_")[-1].isdigit()}


def _logs(ui) -> dict:
    """The encounter log's rounds (none before its file is first written)."""
    return _rounds(ui._read_log())


def _everything(ui) -> dict:
    """All the state an undo must put back."""
    return {
        "combatants": [_combat_data(c) for c in ui.characters],
        "order": [c["name"] for c in ui.initiative_order],
        "turn": ui.current_turn_idx,
        "round": ui.round_number,
        "round_label": ui.round_label.text(),
        "logs": _logs(ui),
    }


def _damage(ui, amount: int):
    ui.damage_type_combo.setCurrentIndex(1)  # reset to "none" after every hit
    ui.damage_input.setText(str(amount))
    ui._apply_damage()


def test_undo_damage_puts_everything_back(fight):
    ui, _, tiger = fight
    before = _everything(ui)
    _damage(ui, 20)  # 30 HP Tiger -> 10, Bloodied
    assert tiger["hp"] == 10 and "Bloodied" in tiger["conditions"]

    ui._undo_last()

    assert _everything(ui) == before
    assert ui.history == []


def test_undo_takes_back_operations_newest_first(fight):
    # The old bug: logging an Action wrote a line but no undo step, so undoing
    # the damage before it deleted the Action's line and left the damage's.
    ui, pirate, tiger = fight
    start = _everything(ui)
    _damage(ui, 5)
    after_damage = _everything(ui)
    ui._add_action_use("Action")

    ui._undo_last()
    assert _everything(ui) == after_damage
    assert not pirate.get("action_uses")

    ui._undo_last()
    assert _everything(ui) == start
    assert tiger["hp"] == 30


def test_an_undone_hit_leaves_the_log(fight):
    # The log is replayed to rebuild the party next session, so an undone
    # action must not stay in it.
    ui, _, _ = fight
    ui._add_action_use("Action")
    _damage(ui, 5)
    ui._add_action_use("Action")
    ui._undo_last()
    ui._undo_last()

    assert _logs(ui)["round_1"] == [
        {"text": "[Pirate's turn] Pirate uses Action", "character": "Pirate"}
    ]


def test_undo_reverts_the_combatant_it_changed_whoever_is_selected(fight):
    ui, pirate, tiger = fight
    ui._cast_spell_slot_level(1)
    ui._select_character(tiger)

    ui._undo_last()

    assert pirate["spell_slots"] == {1: 2}
    assert pirate["stats"]["spell_slots_used"] == 0


def test_undo_with_no_selection_still_works(fight):
    ui, pirate, _ = fight
    ui._cast_spell_slot_level(1)
    ui._clear_selection()

    ui._undo_last()

    assert pirate["spell_slots"] == {1: 2}


def test_one_undo_takes_back_damage_to_every_target(fight):
    ui, pirate, tiger = fight
    ui._select_target_character(pirate, additive=True)
    before = _everything(ui)
    _damage(ui, 20)
    assert pirate["hp"] == 13 and tiger["hp"] == 10

    ui._undo_last()

    assert _everything(ui) == before


def test_one_undo_takes_back_a_whole_spell_cast(fight):
    # Hold Person on the Tiger: the caster spends an Action and starts
    # Concentrating with a 1-minute timer, the Tiger gets the spell's badge.
    ui, pirate, tiger = fight
    before = _everything(ui)
    ui._apply_cast_spell(SpellFactory.create("Hold Person"))
    assert "Hold Person" in tiger["conditions"]
    assert "Concentrating" in pirate["conditions"]
    assert pirate["active_spells"]

    ui._undo_last()

    assert _everything(ui) == before
    assert len(ui.history) == 0


def test_undo_next_turn(fight):
    ui, pirate, tiger = fight
    pirate["active_spells"] = [
        {"name": "Bless", "time_left": 6, "duration": 60, "concentration": False}
    ]
    ui._advance_turn()  # Tiger's turn
    ui._add_action_use("Action")
    before = _everything(ui)

    ui._advance_turn()  # Round 2: Bless runs out, the Pirate's tallies reset
    assert ui.round_number == 2 and pirate["active_spells"] == []

    ui._undo_last()

    assert _everything(ui) == before
    assert ui._next_turn_btn.text() == "Next Round"


def test_undo_back_across_a_round(fight):
    ui, _, tiger = fight
    start = _everything(ui)
    _damage(ui, 5)
    ui._advance_turn()
    ui._advance_turn()
    _damage(ui, 3)

    for _ in range(4):
        ui._undo_last()

    assert _everything(ui) == start
    assert tiger["hp"] == 30
    assert "round_2" not in _logs(ui)


def test_undo_an_added_combatant(fight):
    ui, pirate, _ = fight
    ui._add_ad_hoc_combatant("Wooden Door", hp=15, ac=12)
    door = ui.characters[-1]
    ui._select_target_character(door)
    _damage(ui, 4)

    ui._undo_last()
    ui._undo_last()

    assert [c["name"] for c in ui.characters] == ["Pirate", "Tiger"]
    assert [c["name"] for c in ui.initiative_order] == ["Pirate", "Tiger"]
    assert ui.target_characters == []
    assert ui.selected_character is pirate


def test_right_click_removing_a_condition_is_undoable(fight):
    ui, _, tiger = fight
    tiger["conditions"].append("Prone")
    ui._remove_condition_from(tiger, "Prone")

    ui._undo_last()

    assert tiger["conditions"] == ["Prone"]


def test_operations_that_change_nothing_leave_no_undo_step(fight):
    ui, _, tiger = fight
    ui.damage_input.setText("2d6")
    ui._apply_damage()
    ui._remove_condition_from(tiger, "Prone")
    ui._clear_selection()
    ui._add_action_use("Action")
    assert ui.history == []


def test_undo_with_nothing_to_undo_does_nothing(fight):
    ui, _, _ = fight
    before = _everything(ui)
    ui._undo_last()
    assert _everything(ui) == before


def test_nothing_is_recorded_before_combat(tmp_path):
    ui = make_ui(tmp_path, [Pirate()])
    ui._add_ad_hoc_combatant("Wooden Door")
    assert ui.history == []


def test_a_qt_signals_extra_argument_is_dropped(fight):
    # clicked passes `checked`; the decorated methods don't take it.
    ui, _, _ = fight
    ui._advance_turn(False)
    assert ui.current_turn_idx == 1
