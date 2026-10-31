"""The combat UI's Settings (settings.py, DialogsMixin._show_settings_dialog):
each one's default is how the window behaved before it existed, and each
changes what happens when the turn changes (TurnsMixin._on_turn_changed) or
damage is applied (DamageMixin._do_apply_damage)."""

import pytest
from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QCheckBox, QDialog, QMessageBox, QPushButton

from Combat.Combatants import Pirate, Tiger
from Combat.CombatUIQt.settings import SETTING_SECTIONS, CombatSettings
from tests._combat_ui import make_ui, open_dialog


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    """A modal dialog would block the test forever; fail it instead."""

    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)


def _grouped_tiger(name: str):
    tiger = Tiger()
    tiger.set_name(name)
    tiger.initiative_group = "Tigers"
    return tiger


@pytest.fixture
def fight(tmp_path):
    """A Pirate (15), Tiger 1 and Tiger 2 (one turn, 12) and a Bandit Pirate
    (5), before combat starts."""
    bandit = Pirate()
    bandit.set_name("Bandit")
    ui = make_ui(
        tmp_path,
        [Pirate(), _grouped_tiger("Tiger 1"), _grouped_tiger("Tiger 2"), bandit],
    )
    pirate, tiger1, tiger2, bandit = ui.characters
    ui._initiative_inputs[id(pirate)].setText("15")
    ui._initiative_inputs[id(tiger1)].setText("12")
    ui._initiative_inputs[id(bandit)].setText("5")
    return ui, pirate, tiger1, tiger2, bandit


def test_the_defaults_keep_the_window_as_it_was():
    # "Source follows the turn", "Clear targets when the turn changes" and
    # "Skip dead combatants' turns" were asked for as new defaults.
    assert CombatSettings() == CombatSettings(
        source_follows_turn=True,
        clear_targets_on_turn=True,
        restart_player_timer_on_turn=False,
        scroll_to_active_card=True,
        skip_dead_turns=True,
        remember_damage_type=True,
        reset_damage_type_after_hit=True,
        ask_concentration_saves=True,
        monsters_roll_concentration=False,
        focus_damage_on_target=False,
        ask_initiative_ties=True,
        show_more_controls=False,
    )


def test_every_setting_is_in_the_dialog_once():
    shown = [info.name for _, infos in SETTING_SECTIONS for info in infos]
    assert sorted(shown) == sorted(vars(CombatSettings()))


def test_starting_combat_makes_the_first_turn_the_source(fight):
    ui, pirate, *_ = fight
    ui._start_combat()
    assert ui.selected_character is pirate
    assert ui.selected_label.text() == "Source: Pirate"


def test_a_groups_turn_makes_its_first_member_the_source(fight):
    ui, pirate, tiger1, tiger2, bandit = fight
    ui._start_combat()
    ui._advance_turn()
    assert ui._current_turn_group() == [tiger1, tiger2]
    assert ui.selected_character is tiger1
    ui._advance_turn()
    assert ui.selected_character is bandit
    ui._advance_turn()  # round 2
    assert ui.selected_character is pirate


def test_a_clicked_source_lasts_until_the_turn_changes(fight):
    ui, pirate, tiger1, tiger2, _ = fight
    ui._start_combat()
    ui._select_character(tiger2)
    ui._select_target_character(pirate)
    ui.damage_type_combo.setCurrentIndex(1)
    ui.damage_input.setText("3")
    ui._apply_damage()
    assert ui.selected_character is tiger2
    ui._advance_turn()
    assert ui.selected_character is tiger1


def test_turned_off_the_source_stays_where_it_was_put(fight):
    ui, pirate, tiger1, _, bandit = fight
    ui.settings.source_follows_turn = False
    ui._start_combat()
    assert ui.selected_character is None
    ui._select_character(bandit)
    ui._advance_turn()
    assert ui.selected_character is bandit


def test_undoing_next_turn_moves_the_source_back(fight):
    ui, pirate, tiger1, *_ = fight
    ui._start_combat()
    ui._advance_turn()
    assert ui.selected_character is tiger1
    ui._undo_last()
    assert ui.selected_character is pirate


def test_undoing_anything_else_keeps_a_clicked_source(fight):
    ui, pirate, _, tiger2, _ = fight
    ui._start_combat()
    ui._select_character(tiger2)
    ui._select_target_character(pirate)
    ui.damage_type_combo.setCurrentIndex(1)
    ui.damage_input.setText("3")
    ui._apply_damage()
    ui._undo_last()
    assert ui.selected_character is tiger2


def test_the_settings_button_opens_the_dialog(fight, monkeypatch):
    ui, *_ = fight
    button = next(
        b for b in ui._window.findChildren(QPushButton) if b.text() == "Settings"
    )
    dlg = open_dialog(monkeypatch, button.click)
    assert dlg.windowTitle() == "Settings"


def test_the_checkbox_changes_and_saves_the_setting(fight, monkeypatch, tmp_path):
    ui, pirate, _, _, bandit = fight
    store = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    ui._settings_store = store
    ui._start_combat()
    ui._select_character(bandit)
    dlg = open_dialog(monkeypatch, ui._show_settings_dialog)
    box = dlg.findChild(QCheckBox, "source_follows_turn")
    assert box is not None and box.isChecked()

    box.setChecked(False)
    assert ui.settings.source_follows_turn is False
    assert store.value("source_follows_turn", type=bool) is False
    assert ui.selected_character is bandit

    # Turning it on makes whoever's turn it is the source straight away.
    box.setChecked(True)
    assert ui.settings.source_follows_turn is True
    assert store.value("source_follows_turn", type=bool) is True
    assert ui.selected_character is pirate


def test_saved_settings_load_back(tmp_path):
    store = QSettings(str(tmp_path / "settings.ini"), QSettings.Format.IniFormat)
    changed = CombatSettings(clear_targets_on_turn=True, scroll_to_active_card=False)
    changed.save(store)
    loaded = CombatSettings()
    loaded.load(store)
    assert loaded == changed


def test_clear_targets_when_the_turn_changes(fight):
    ui, pirate, tiger1, _, bandit = fight
    ui._start_combat()
    ui._select_target_character(bandit)
    ui._advance_turn()
    assert ui.target_characters == [], "on by default"
    assert ui.target_label.text() == "Target: None"

    ui.settings.clear_targets_on_turn = False
    ui._select_target_character(bandit)
    ui._advance_turn()
    assert ui.target_characters == [bandit]


def test_restart_the_player_timer_each_turn(fight):
    ui, pirate, tiger1, _, _ = fight
    pirate["_is_player"] = True
    ui.settings.restart_player_timer_on_turn = True
    ui._start_combat()
    assert ui._player_timer_running, "a player's turn starts the timer"
    ui._player_elapsed_seconds = 42
    ui._advance_turn()
    assert not ui._player_timer_running and ui._player_elapsed_seconds == 0
    ui._advance_turn()
    ui._advance_turn()  # round 2, the Pirate again
    assert ui._player_timer_running
    ui._pause_player_timer()


def test_scroll_to_the_active_card(fight, monkeypatch):
    ui, *_ = fight
    scrolled = []
    monkeypatch.setattr(ui._scroll_area, "ensureWidgetVisible", scrolled.append)
    ui._start_combat()
    assert scrolled
    scrolled.clear()
    ui.settings.scroll_to_active_card = False
    ui._advance_turn()
    assert scrolled == []


def _hit(ui, target, amount=3):
    ui._select_target_character(target)
    ui.damage_type_combo.setCurrentIndex(1)
    ui.damage_input.setText(str(amount))
    ui._apply_damage()


def test_the_damage_type_after_a_hit(fight):
    ui, _, tiger1, *_ = fight
    ui._start_combat()
    _hit(ui, tiger1)
    assert ui.damage_type_combo.currentIndex() == 1, "the source's remembered type"
    ui.settings.remember_damage_type = False
    _hit(ui, tiger1)
    assert ui.damage_type_combo.currentIndex() == 0, "reset by default"
    ui.settings.reset_damage_type_after_hit = False
    _hit(ui, tiger1)
    assert ui.damage_type_combo.currentIndex() == 1


def test_concentration_saves_can_be_left_to_the_gm(fight):
    ui, _, tiger1, *_ = fight
    ui._start_combat()
    tiger1["conditions"].append("Concentrating")
    _hit(ui, tiger1)
    assert tiger1["concentration_checks"] == [10]

    ui._settle_concentration(tiger1, 10, kept=True)
    ui.settings.ask_concentration_saves = False
    _hit(ui, tiger1)
    assert "concentration_checks" not in tiger1
    assert "Concentrating" in tiger1["conditions"]
