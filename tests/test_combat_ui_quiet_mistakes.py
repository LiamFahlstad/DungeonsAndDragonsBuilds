"""The mistakes a GM makes without noticing mid-fight, which the combat UI now
heads off: Enter skipping resistances, a cast spell not spending its slot, an
action that silently does nothing, and pressing Next past dead monsters."""

import pytest
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QTreeWidget,
)

from CharacterContent.Spells.SpellFactory import SpellFactory
from Combat.Combatants import Pirate, Tiger
from Combat.CombatUIQt.spells_mixin import spell_slot_choices
from Core.Definitions import DamageType
from tests._combat_ui import make_ui, open_dialog

FIRE = DamageType.FIRE.value


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    """A modal dialog would block the test forever; fail it instead."""

    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)


def _named(combatant, name: str, group: str | None = None):
    combatant.set_name(name)
    if group is not None:
        combatant.initiative_group = group
    return combatant


def _start(ui, *initiatives: int):
    """Start combat with these initiatives, in card order."""
    for char, value in zip(ui.characters, initiatives):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()


@pytest.fixture
def fight(tmp_path):
    """A Pirate (15), a 30 HP Tiger (10) and a Bandit (5), the Pirate's turn,
    with the Tiger targeted."""
    ui = make_ui(tmp_path, [Pirate(), Tiger(), _named(Pirate(), "Bandit")])
    _start(ui, 15, 10, 5)
    pirate, tiger, bandit = ui.characters
    ui._select_target_character(tiger)
    return ui, pirate, tiger, bandit


def _button(ui, text: str) -> QPushButton:
    return next(b for b in ui._window.findChildren(QPushButton) if b.text() == text)


def _set_damage(ui, amount: str, damage_type: str = FIRE):
    ui.damage_type_combo.setCurrentIndex(ui.damage_type_combo.findData(damage_type))
    ui.damage_input.setText(amount)


# ---------------------------------------------------------------------------
# 1. Resistances count unless asked not to


@pytest.fixture
def fire_resistant_tiger(fight):
    ui, _, tiger, _ = fight
    tiger["damage_resistances"] = [{"damage_types": [FIRE]}]
    return ui, tiger


def test_enter_in_the_damage_field_counts_resistance(fire_resistant_tiger):
    ui, tiger = fire_resistant_tiger
    _set_damage(ui, "10")
    ui.damage_input.returnPressed.emit()
    assert tiger["hp"] == tiger["max_hp"] - 5


def test_the_apply_button_counts_resistance(fire_resistant_tiger):
    ui, tiger = fire_resistant_tiger
    _set_damage(ui, "10")
    _button(ui, "Apply").click()
    assert tiger["hp"] == tiger["max_hp"] - 5


def test_ignore_resist_applies_the_amount_typed(fire_resistant_tiger):
    ui, tiger = fire_resistant_tiger
    _set_damage(ui, "10")
    _button(ui, "Ignore Resist").click()
    assert tiger["hp"] == tiger["max_hp"] - 10


# ---------------------------------------------------------------------------
# 2. Cast Spell spends the slot


def _spell_dialog(ui, monkeypatch, spell_name: str):
    """The Cast Spell dialog for the source, with spell_name picked. It's
    found in the caster's own list when it's there, as that comes first."""
    dlg = open_dialog(monkeypatch, ui._show_cast_spell_dialog)
    tree = dlg.findChild(QTreeWidget)
    assert tree is not None
    for i in range(tree.topLevelItemCount()):
        category = tree.topLevelItem(i)
        for j in range(category.childCount()):
            if category.child(j).text(0) == spell_name:
                tree.setCurrentItem(category.child(j))
                return dlg
    raise AssertionError(f"{spell_name} isn't listed")


def _slot_combo(dlg) -> QComboBox:
    combo = dlg.findChild(QComboBox)
    assert combo is not None
    return combo


def _cast_button(dlg) -> QPushButton:
    return next(b for b in dlg.findChildren(QPushButton) if b.text().startswith("Cast"))


@pytest.fixture
def caster(fight):
    """The Pirate as the source, knowing Hold Person (level 2) and Fire Bolt
    (a cantrip), with two level 2 slots and one level 3 slot."""
    ui, pirate, tiger, _ = fight
    pirate["_spell_objects"] = {
        name: SpellFactory.create(name) for name in ("Hold Person", "Fire Bolt")
    }
    pirate["spell_slots"] = {1: 1, 2: 2, 3: 1}
    ui._select_character(pirate)
    return ui, pirate, tiger


def _log_text(ui) -> str:
    return str(ui._read_log())


def test_the_casters_own_spells_come_first(caster, monkeypatch):
    ui, _, _ = caster
    dlg = open_dialog(monkeypatch, ui._show_cast_spell_dialog)
    tree = dlg.findChild(QTreeWidget)
    own = tree.topLevelItem(0)
    assert own.text(0) == "Pirate's Spells"
    assert own.isExpanded()
    assert [own.child(i).text(0) for i in range(own.childCount())] == [
        "Fire Bolt",
        "Hold Person",
    ]
    # Every other spell stays reachable, for a scroll or a surprise.
    assert tree.topLevelItemCount() > 1


def test_a_caster_with_no_spell_list_gets_the_plain_list(fight, monkeypatch):
    ui, pirate, _, _ = fight
    ui._select_character(pirate)
    dlg = open_dialog(monkeypatch, ui._show_cast_spell_dialog)
    assert dlg.findChild(QTreeWidget).topLevelItem(0).text(0) == "Cantrips"


def test_casting_spends_the_lowest_slot_that_fits(caster, monkeypatch):
    ui, pirate, tiger = caster
    dlg = _spell_dialog(ui, monkeypatch, "Hold Person")
    assert _slot_combo(dlg).currentData() == 2
    _cast_button(dlg).click()
    assert pirate["spell_slots"] == {1: 1, 2: 1, 3: 1}
    assert "Hold Person" in tiger["conditions"]
    assert "at level" not in _log_text(ui)


def test_a_higher_slot_upcasts(caster, monkeypatch):
    ui, pirate, _ = caster
    dlg = _spell_dialog(ui, monkeypatch, "Hold Person")
    combo = _slot_combo(dlg)
    combo.setCurrentIndex(combo.findData(3))
    _cast_button(dlg).click()
    assert pirate["spell_slots"] == {1: 1, 2: 2, 3: 0}
    assert "casts Hold Person at level 3" in _log_text(ui)


def test_a_cantrip_spends_no_slot(caster, monkeypatch):
    ui, pirate, _ = caster
    dlg = _spell_dialog(ui, monkeypatch, "Fire Bolt")
    assert not _slot_combo(dlg).isEnabled()
    _cast_button(dlg).click()
    assert pirate["spell_slots"] == {1: 1, 2: 2, 3: 1}


def test_casting_free_of_a_slot_can_be_chosen(caster, monkeypatch):
    ui, pirate, _ = caster
    dlg = _spell_dialog(ui, monkeypatch, "Hold Person")
    combo = _slot_combo(dlg)
    combo.setCurrentIndex(combo.count() - 1)
    assert combo.currentData() is None
    _cast_button(dlg).click()
    assert pirate["spell_slots"] == {1: 1, 2: 2, 3: 1}


def test_out_of_slots_says_so_on_the_button(caster, monkeypatch):
    ui, pirate, _ = caster
    pirate["spell_slots"] = {1: 3, 2: 0, 3: 0}
    dlg = _spell_dialog(ui, monkeypatch, "Hold Person")
    assert _cast_button(dlg).text() == "Cast without a slot"
    assert any(
        label.text() == "No slot of level 2 or higher left."
        for label in dlg.findChildren(QLabel)
    )
    _cast_button(dlg).click()
    assert pirate["spell_slots"] == {1: 3, 2: 0, 3: 0}


def test_undoing_a_cast_gives_the_slot_back(caster, monkeypatch):
    ui, pirate, tiger = caster
    _cast_button(_spell_dialog(ui, monkeypatch, "Hold Person")).click()
    ui._undo_last()
    assert pirate["spell_slots"] == {1: 1, 2: 2, 3: 1}
    assert "Hold Person" not in tiger["conditions"]
    assert len(ui.history) == 0, "the cast and its slot are one step"


def test_the_slot_is_spent_only_if_the_cast_happens(caster):
    ui, pirate, _ = caster
    ui.target_characters = []
    ui._apply_cast_spell(SpellFactory.create("Hold Person"), slot_level=2)
    assert "needs a target" in _status(ui)
    assert pirate["spell_slots"] == {1: 1, 2: 2, 3: 1}


def test_slot_choices():
    char = {"spell_slots": {1: 2, 2: 0, 3: 1, 4: 1}}
    assert [level for _, level in spell_slot_choices(char, 2)] == [3, 4, None]
    assert [level for _, level in spell_slot_choices(char, 0)] == [None]
    assert spell_slot_choices({"spell_slots": {}}, 2) == [("No slots tracked", None)]
    assert spell_slot_choices({}, 2) == [("No slots tracked", None)]


# ---------------------------------------------------------------------------
# 3. Nothing fails silently


def _status(ui) -> str:
    return ui._status_label.text()


def test_a_sum_is_applied_as_its_total(fight):
    ui, _, tiger, _ = fight
    _set_damage(ui, "8+5")
    ui._apply_damage_checked()
    assert tiger["hp"] == tiger["max_hp"] - 13
    ui.heal_input.setText("2+1")
    ui._apply_heal()
    assert tiger["hp"] == tiger["max_hp"] - 10
    ui.temp_hp_input.setText("3+3")
    ui._apply_temp_hp()
    assert tiger["temp_hp"] == 6


@pytest.mark.parametrize("field", ["damage", "heal", "temp_hp"])
def test_no_target_says_so(fight, field):
    ui, _, tiger, _ = fight
    ui.target_characters = []
    _set_damage(ui, "5")
    ui.heal_input.setText("5")
    ui.temp_hp_input.setText("5")
    {
        "damage": ui._apply_damage_checked,
        "heal": ui._apply_heal,
        "temp_hp": ui._apply_temp_hp,
    }[field]()
    assert "pick a target" in _status(ui)
    assert tiger["hp"] == tiger["max_hp"]
    assert ui.history == []


def test_an_amount_that_isnt_one_says_so(fight):
    ui, _, tiger, _ = fight
    _set_damage(ui, "2d6")
    ui._apply_damage_checked()
    assert "'2d6' isn't an amount" in _status(ui)
    assert tiger["hp"] == tiger["max_hp"]


def test_an_empty_amount_says_so(fight):
    ui, _, _, _ = fight
    ui.heal_input.setText("")
    ui._apply_heal()
    assert "no amount" in _status(ui)


def test_a_missing_damage_type_says_so_without_a_popup(fight):
    ui, _, tiger, _ = fight
    ui.damage_input.setText("5")
    ui._apply_damage_checked()  # the fixture fails on a popup
    assert "pick a damage type" in _status(ui)
    assert tiger["hp"] == tiger["max_hp"]


def test_conditions_with_no_target_say_so(fight):
    ui, _, _, _ = fight
    ui.target_characters = []
    ui._add_condition()
    assert "pick a target" in _status(ui)
    ui._clear_status()
    ui._remove_condition()
    assert "pick a target" in _status(ui)


def test_no_source_says_so(fight):
    ui, _, _, _ = fight
    ui._clear_selection()
    for action in (
        lambda: ui._add_action_use("Action"),
        lambda: ui._remove_action_use("Action"),
        lambda: ui._cast_spell_slot_level(1),
        ui._regain_spell_slot,
        ui._add_visibility,
        ui._remove_visibility,
    ):
        ui._clear_status()
        action()
        assert "pick a source" in _status(ui)


def test_a_used_up_slot_level_says_so(fight):
    ui, pirate, _, _ = fight
    pirate["spell_slots"] = {3: 0}
    ui._select_character(pirate)
    ui._cast_spell_slot_level(3)
    assert _status(ui) == "Nothing spent: Pirate has no level 3 slots left."


def test_something_working_clears_the_message(fight):
    ui, _, tiger, _ = fight
    _set_damage(ui, "oops")
    ui._apply_damage_checked()
    assert _status(ui)
    _set_damage(ui, "4")
    ui._apply_damage_checked()
    assert _status(ui) == ""
    assert tiger["hp"] == tiger["max_hp"] - 4


def test_a_message_never_moves_the_buttons(fight):
    ui, _, _, _ = fight
    label = ui._status_label
    empty_height = label.height(), label.minimumHeight(), label.maximumHeight()
    ui._show_status("Nothing applied: a message long enough to wrap " * 2)
    assert (label.height(), label.minimumHeight(), label.maximumHeight()) == (
        empty_height
    )
    assert label.minimumHeight() == label.maximumHeight() > 0


def test_the_message_goes_away_by_itself(fight):
    ui, _, _, _ = fight
    ui._show_status("Nothing applied")
    assert ui._status_timer.isActive() and ui._status_timer.isSingleShot()
    ui._status_timer.timeout.emit()
    assert _status(ui) == ""


# ---------------------------------------------------------------------------
# 5. Dead combatants' turns pass by themselves


def _turn_name(ui) -> str:
    return ui.initiative_order[ui.current_turn_idx]["name"]


def test_next_skips_a_dead_monster(fight):
    ui, _, tiger, bandit = fight
    tiger["hp"] = 0
    ui._advance_turn()
    assert ui.selected_character is bandit
    assert _turn_name(ui) == "Bandit (Pirate)"
    assert ui.round_number == 1


def test_skipping_past_the_last_turn_starts_the_next_round(fight):
    ui, pirate, _, bandit = fight
    bandit["hp"] = 0
    ui._advance_turn()  # the Tiger
    ui._advance_turn()  # past the Bandit
    assert ui.round_number == 2
    assert ui.round_label.text() == "Round 2"
    assert _turn_name(ui) == "Pirate"
    assert "--- Round 2 ---" in _log_text(ui)


def test_a_skip_is_one_undo(fight):
    ui, pirate, tiger, _ = fight
    tiger["hp"] = 0
    ui._advance_turn()
    ui._undo_last()
    assert _turn_name(ui) == "Pirate"
    assert ui.history == []


def test_a_group_is_skipped_only_when_all_of_it_is_dead(tmp_path):
    ui = make_ui(
        tmp_path,
        [
            Pirate(),
            _named(Tiger(), "Tiger 1", "Tigers"),
            _named(Tiger(), "Tiger 2", "Tigers"),
            _named(Pirate(), "Bandit"),
        ],
    )
    pirate, tiger1, tiger2, bandit = ui.characters
    ui._initiative_inputs[id(pirate)].setText("15")
    ui._initiative_inputs[id(tiger1)].setText("10")
    ui._initiative_inputs[id(bandit)].setText("5")
    ui._start_combat()

    tiger1["hp"] = 0
    ui._advance_turn()
    assert ui._current_turn_group() == [tiger1, tiger2], "Tiger 2 is still up"

    ui._undo_last()
    tiger1["hp"] = tiger2["hp"] = 0
    ui._advance_turn()
    assert ui._current_turn_group() == [bandit]


def test_a_dying_player_still_gets_a_turn(fight):
    ui, _, tiger, _ = fight
    tiger["_is_player"] = True
    tiger["hp"] = 0
    assert ui._char_death_state(tiger) == "dying"
    ui._advance_turn()
    assert _turn_name(ui) == "Tiger"


def test_a_player_dead_of_failed_saves_is_skipped(fight):
    ui, _, tiger, _ = fight
    tiger["_is_player"] = True
    tiger["hp"] = 0
    tiger["death_saves_fail"] = 3
    ui._advance_turn()
    assert _turn_name(ui) == "Bandit (Pirate)"


def test_durations_count_skipped_turns(fight):
    ui, pirate, tiger, bandit = fight
    ui._select_target_character(bandit)
    # Given by the Tiger, so it ends when the Tiger's turn starts.
    ui._select_character(tiger)
    ui._add_custom_condition("Marked", {"until": "start", "of": "source"})
    ui._select_character(pirate)
    assert "Marked" in bandit["conditions"]
    tiger["hp"] = 0
    ui._advance_turn()
    assert _turn_name(ui) == "Bandit (Pirate)"
    assert "Marked" not in bandit["conditions"]


def test_a_skipped_turn_resets_its_action_tallies_like_any_other(fight):
    ui, _, tiger, _ = fight
    tiger["hp"] = 0
    tiger["action_uses"] = {"Reaction": 1}
    ui._advance_turn()
    assert tiger["action_uses"] == {}


def test_nobody_alive_ends_after_one_lap(fight):
    ui, pirate, tiger, bandit = fight
    pirate["hp"] = tiger["hp"] = bandit["hp"] = 0
    ui._advance_turn()  # must return, not spin
    assert (ui.round_number, _turn_name(ui)) == (2, "Pirate")


def test_the_setting_turned_off_stops_on_the_dead(fight):
    ui, _, tiger, _ = fight
    ui.settings.skip_dead_turns = False
    tiger["hp"] = 0
    ui._advance_turn()
    assert _turn_name(ui) == "Tiger"


def test_previous_skips_the_dead_too(fight):
    ui, _, tiger, _ = fight
    tiger["hp"] = 0
    ui._advance_turn()  # past the dead Tiger, to the Bandit
    ui._add_action_use("Action")  # so Previous steps back, not undoes the Next
    ui._previous_turn()
    assert _turn_name(ui) == "Pirate"


def test_previous_stops_at_the_first_turn(tmp_path):
    ui = make_ui(tmp_path, [Pirate(), Tiger(), _named(Pirate(), "Bandit")])
    _start(ui, 15, 10, 5)
    pirate, tiger, _ = ui.characters
    ui.settings.skip_dead_turns = False
    ui._advance_turn()
    ui._advance_turn()  # the Bandit's turn
    ui.settings.skip_dead_turns = True
    pirate["hp"] = tiger["hp"] = 0
    ui._add_action_use("Action")
    ui._previous_turn()
    assert (ui.round_number, _turn_name(ui)) == (1, "Pirate")
