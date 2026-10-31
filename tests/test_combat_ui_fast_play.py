"""Combat at the table's pace: typing what you mean in one field, monsters'
turns played from the turn column with no dialog, the players' screen, and
fewer clicks and popups all round. The monsters' abilities are stated here in
the words of a real stat block, not read from one, so a stat-block edit can't
change what these check."""

import json
import random

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTreeWidget,
)

from CharacterContent.Spells.SpellFactory import SpellFactory
from Builds.Characters.Y2024_Artificer_Cartographer_ObmarStalskagg import (
    Y2024ArtificerCartographerObmarStalskaggCharacterBuilder as Obmar,
)
from Combat.Combatants import Pirate, Tiger
from Combat.Definitions import Action
from Combat.CombatUIQt.player_view import player_view_rows
from Combat.CombatUIQt.monster_actions import parse_action
from Combat.CombatUIQt.settings import SETTING_SECTIONS
from Combat.EncounterLogs import PLAYER_SAVES_KEY, LogJSONEncoder
from Core.Definitions import DamageType
from Model.Creatures.Combatants import DamageTypeEntry
from tests._combat_ui import make_ui, open_dialog

FIRE = DamageType.FIRE.value
SLASHING = DamageType.SLASHING.value
POISON = DamageType.POISON.value

BITE = {
    "name": "Bite",
    "description": "Melee Attack Roll: +5, reach 5 ft. Hit: 7 (1d8 + 3) Piercing damage.",
}
FLAIL = {
    "name": "Flail",
    "description": "Melee Attack Roll: +5, reach 5 ft. Hit: 5 (1d4 + 3) Slashing damage"
    " plus 2 (1d4) Fire damage.",
}
BREATH = {
    "name": "Fire Breath (Recharge 5\N{EN DASH}6)",
    "description": "Dexterity Saving Throw: DC 14, each creature in a 30-foot Cone."
    " Failure: 27 (6d8) Fire damage. Success: Half damage.",
}
SCREECH = {
    "name": "Screech (1/Day)",
    "description": "Wisdom Saving Throw: DC 12, each creature. Failure: Frightened.",
}
MULTIATTACK = {"name": "Multiattack", "description": "It makes two Bite attacks."}
LASH = {
    "name": "Lash",
    "description": "Melee Attack Roll: +5, reach 5 ft. Hit: 4 (1d4 + 2) Slashing damage.",
}
WING = {
    "name": "Wing Buffet (Costs 2 Actions)",
    "description": "Dexterity Saving Throw: DC 14, each creature. Failure: Prone.",
}
REGENERATION = {
    "name": "Regeneration",
    "description": "It regains 10 Hit Points at the start of each of its turns.",
}


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
    for char, value in zip(ui.characters, initiatives):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()


@pytest.fixture
def fight(tmp_path):
    """A Pirate (15), a 30 HP Tiger (10) and a Bandit (5), the Pirate's turn
    and the Pirate the source, with the Tiger targeted."""
    ui = make_ui(tmp_path, [Pirate(), Tiger(), _named(Pirate(), "Bandit")])
    _start(ui, 15, 10, 5)
    pirate, tiger, bandit = ui.characters
    ui._select_target_character(tiger)
    return ui, pirate, tiger, bandit


@pytest.fixture
def dragon(fight):
    """The Pirate has a dragon's abilities, and is the source."""
    ui, pirate, tiger, bandit = fight
    pirate.update(
        actions=[MULTIATTACK, BITE, FLAIL, BREATH, SCREECH],
        legendary_actions=[LASH, WING],
        legendary_resistances=3,
        traits=[REGENERATION],
    )
    ui._refresh_views()
    return ui, pirate, tiger, bandit


def _status(ui) -> str:
    return ui._status_label.text()


def _button(parent, text: str) -> QPushButton:
    return next(b for b in parent.findChildren(QPushButton) if b.text() == text)


def _log_text(ui) -> str:
    return str(ui._read_log())


def _damage_field(ui, text: str):
    ui.damage_input.setText(text)
    ui.damage_input.returnPressed.emit()


# ---------------------------------------------------------------------------
# 6. The damage type is typed with the amount, and remembered


def test_a_typed_type_needs_no_dropdown(fight):
    ui, _, tiger, _ = fight
    assert ui.damage_type_combo.currentData() is None
    _damage_field(ui, "12 fi")
    assert tiger["hp"] == tiger["max_hp"] - 12
    assert "takes 12 Fire damage" in _log_text(ui)


def test_a_type_shows_in_the_dropdown_as_it_is_typed(fight):
    ui, *_ = fight
    ui.damage_input.setText("12 fi")
    assert ui.damage_type_combo.currentData() == FIRE


def test_each_source_remembers_its_damage_type(fight):
    ui, pirate, tiger, bandit = fight
    _damage_field(ui, "3 fi")
    assert ui.damage_type_combo.currentData() == FIRE

    ui._select_character(bandit)
    assert ui.damage_type_combo.currentData() is None, "not the Pirate's type"

    ui._select_target_character(tiger)
    _damage_field(ui, "3 sl")
    ui._select_character(pirate)
    assert ui.damage_type_combo.currentData() == FIRE
    _damage_field(ui, "4")
    assert "takes 4 Fire damage" in _log_text(ui)


def test_with_nothing_remembered_a_type_is_still_needed(fight):
    ui, _, tiger, _ = fight
    _damage_field(ui, "5")
    assert "pick a damage type" in _status(ui)
    assert tiger["hp"] == tiger["max_hp"]


def test_a_type_that_doesnt_exist_says_so(fight):
    ui, _, tiger, _ = fight
    _damage_field(ui, "5 zz")
    assert "'zz' isn't a damage type" in _status(ui)
    assert tiger["hp"] == tiger["max_hp"]


def test_the_field_empties_so_a_second_enter_cant_hit_again(fight):
    ui, _, tiger, _ = fight
    _damage_field(ui, "5 fi")
    assert ui.damage_input.text() == ""
    ui.damage_input.returnPressed.emit()
    assert tiger["hp"] == tiger["max_hp"] - 5
    assert "no amount" in _status(ui)


def test_a_hit_of_two_types_counts_resistance_on_each(fight):
    ui, _, tiger, _ = fight
    tiger["damage_resistances"] = [DamageTypeEntry(damage_types=[DamageType.FIRE])]
    _damage_field(ui, "10 sl + 10 fi")
    assert tiger["hp"] == tiger["max_hp"] - 15
    assert "takes 10 Slashing damage" in _log_text(ui)
    assert "takes 5 Fire damage" in _log_text(ui)
    ui._undo_last()
    assert tiger["hp"] == tiger["max_hp"], "the whole hit is one undo"
    assert ui.history == []


def test_a_hit_of_two_types_asks_for_one_concentration_save(fight):
    ui, _, tiger, _ = fight
    tiger["conditions"].append("Concentrating")
    _damage_field(ui, "16 sl + 10 fi")
    assert tiger["concentration_checks"] == [13]  # half of 26


# ---------------------------------------------------------------------------
# 7. Half damage on a save


def test_halving_in_the_field(fight):
    ui, _, tiger, _ = fight
    _damage_field(ui, "25/2 fi")
    assert tiger["hp"] == tiger["max_hp"] - 12


def test_saved_halves_every_target_and_lasts_one_hit(fight):
    ui, _, tiger, bandit = fight
    ui._select_target_character(bandit, ctrl=True)
    ui._half_btn.click()
    assert ui._half_btn.isChecked()
    _damage_field(ui, "20 fi")
    assert tiger["hp"] == tiger["max_hp"] - 10
    assert bandit["hp"] == bandit["max_hp"] - 10
    assert "(saved)" in _log_text(ui)

    assert not ui._half_btn.isChecked()
    _damage_field(ui, "20 fi")
    assert tiger["hp"] == tiger["max_hp"] - 30


def test_a_saved_target_with_resistance_halves_twice(fight):
    ui, _, tiger, _ = fight
    tiger["damage_resistances"] = [DamageTypeEntry(damage_types=[DamageType.FIRE])]
    ui._half_btn.click()
    _damage_field(ui, "25 fi")
    assert tiger["hp"] == tiger["max_hp"] - 6  # 25 -> 12 -> 6


def _saved_toggle(ui, char):
    toggles = [
        b
        for b in ui._card_widgets[id(char)].findChildren(QPushButton)
        if b.objectName() == "savedToggle"
    ]
    return toggles[0] if toggles else None


def test_each_target_of_several_has_its_own_saved_toggle(fight):
    ui, pirate, tiger, bandit = fight
    assert _saved_toggle(ui, tiger) is None, "one target has the panel's button"

    ui._select_target_character(bandit, ctrl=True)
    assert _saved_toggle(ui, pirate) is None, "not a target"
    _saved_toggle(ui, bandit).click()
    _damage_field(ui, "20 fi")
    assert tiger["hp"] == tiger["max_hp"] - 20
    assert bandit["hp"] == bandit["max_hp"] - 10


def test_a_target_dropped_is_no_longer_saved(fight):
    ui, _, tiger, bandit = fight
    ui._select_target_character(bandit, ctrl=True)
    _saved_toggle(ui, bandit).click()
    ui._select_target_character(bandit, ctrl=True)
    assert ui._saved_targets == []
    assert _saved_toggle(ui, tiger) is None


# ---------------------------------------------------------------------------
# 8. Concentration saves on the card


def _concentrating(ui, char):
    char["conditions"].append("Concentrating")
    char["active_spells"] = [
        {"name": "Bless", "time_left": 60, "duration": 60, "concentration": True}
    ]
    ui._select_target_character(char)


def test_a_save_goes_on_the_card_with_no_dialog(fight):
    ui, _, tiger, _ = fight
    _concentrating(ui, tiger)
    _damage_field(ui, "24 fi")  # the fixture fails on a dialog
    card = ui._card_widgets[id(tiger)]
    labels = [label.text() for label in card.findChildren(QLabel)]
    assert any(text.startswith("DC 12 CON (") for text in labels), labels
    for text in ("Roll", "Kept", "Lost"):
        assert _button(card, text).isEnabled()


def test_small_damage_is_dc_10(fight):
    ui, _, tiger, _ = fight
    _concentrating(ui, tiger)
    _damage_field(ui, "3 fi")
    assert tiger["concentration_checks"] == [10]


def test_kept(fight):
    ui, _, tiger, _ = fight
    _concentrating(ui, tiger)
    _damage_field(ui, "3 fi")
    _button(ui._card_widgets[id(tiger)], "Kept").click()
    assert "concentration_checks" not in tiger
    assert "Concentrating" in tiger["conditions"]
    assert tiger["active_spells"]
    assert "keeps concentration (DC 10)" in _log_text(ui)


def test_lost_ends_the_spell(fight):
    ui, _, tiger, _ = fight
    _concentrating(ui, tiger)
    _damage_field(ui, "3 fi")
    _button(ui._card_widgets[id(tiger)], "Lost").click()
    assert "concentration_checks" not in tiger
    assert "Concentrating" not in tiger["conditions"]
    assert not tiger["active_spells"]
    assert "loses concentration (DC 10)" in _log_text(ui)


@pytest.mark.parametrize("d20, kept", [(10, True), (9, False)])
def test_roll_uses_the_con_save(fight, monkeypatch, d20, kept):
    ui, _, tiger, _ = fight
    tiger["Saving Throws"] = {"CON": 2}
    _concentrating(ui, tiger)
    _damage_field(ui, "24 fi")  # DC 12, so a +2 needs a 10
    monkeypatch.setattr(random, "randint", lambda low, high: d20)
    _button(ui._card_widgets[id(tiger)], "Roll").click()
    assert ("Concentrating" in tiger["conditions"]) is kept
    assert f"rolled {d20 + 2}" in _log_text(ui)


def test_a_save_is_one_undo_back_on_the_card(fight):
    ui, _, tiger, _ = fight
    _concentrating(ui, tiger)
    _damage_field(ui, "3 fi")
    _button(ui._card_widgets[id(tiger)], "Lost").click()
    ui._undo_last()
    assert tiger["concentration_checks"] == [10]
    assert "Concentrating" in tiger["conditions"]
    assert tiger["active_spells"]


def test_two_hits_two_saves_and_one_loss_ends_both(fight):
    ui, _, tiger, _ = fight
    _concentrating(ui, tiger)
    _damage_field(ui, "3 fi")
    _damage_field(ui, "24 fi")
    assert tiger["concentration_checks"] == [10, 12]
    ui._settle_concentration(tiger, 10, kept=True)
    assert tiger["concentration_checks"] == [12]
    ui._settle_concentration(tiger, 12, kept=False)
    assert "concentration_checks" not in tiger


def test_losing_concentration_any_other_way_drops_the_save(fight):
    ui, _, tiger, _ = fight
    _concentrating(ui, tiger)
    _damage_field(ui, "3 fi")
    ui._remove_condition_from(tiger, "Concentrating")
    assert "concentration_checks" not in tiger


def test_a_pending_save_survives_a_saved_fight(fight):
    ui, _, tiger, _ = fight
    _concentrating(ui, tiger)
    _damage_field(ui, "3 fi")
    saved = next(c for c in ui._read_log()["combatants"] if c["name"] == "Tiger")
    assert saved["concentration_checks"] == [10]


def test_monsters_can_roll_their_own(fight, monkeypatch):
    ui, _, tiger, _ = fight
    ui.settings.monsters_roll_concentration = True
    _concentrating(ui, tiger)
    monkeypatch.setattr(random, "randint", lambda low, high: 1)
    _damage_field(ui, "3 fi")
    assert "concentration_checks" not in tiger
    assert "Concentrating" not in tiger["conditions"]
    assert "loses concentration (DC 10" in _log_text(ui)


def test_a_player_still_rolls_their_own(fight):
    ui, _, tiger, _ = fight
    ui.settings.monsters_roll_concentration = True
    tiger["_is_player"] = True
    _concentrating(ui, tiger)
    _damage_field(ui, "3 fi")
    assert tiger["concentration_checks"] == [10]


# ---------------------------------------------------------------------------
# 9. The source's actions, in the turn column


def _action(ui, name: str) -> QPushButton:
    return next(
        b
        for b in ui._actions_box.findChildren(QPushButton)
        if b.isVisibleTo(ui._actions_box) and b.text().startswith(name)
    )


def _dice(monkeypatch, *rolls: int):
    """random.randint gives these rolls, in turn."""
    results = iter(rolls)
    monkeypatch.setattr(random, "randint", lambda low, high: next(results))


def test_actions_show_for_the_source_with_their_numbers(dragon):
    ui, *_ = dragon
    assert _action(ui, "Bite").text() == "Bite\n+5  1d8 + 3 Piercing"
    assert (
        _action(ui, "Fire Breath").text().endswith("DC 14 Dex  6d8 Fire  half on save")
    )
    texts = [label.text() for label in ui._actions_box.findChildren(QLabel)]
    assert any(text.startswith("Multiattack: It makes two Bite") for text in texts)


def test_a_player_source_shows_no_actions(fight):
    ui, *_ = fight
    ui._refresh_views()
    assert ui._actions_box.findChildren(QPushButton) == []


def test_a_hit_fills_in_the_damage_for_enter_to_apply(dragon, monkeypatch):
    ui, _, tiger, _ = dragon
    tiger["ac"] = 13
    _dice(monkeypatch, 10, 4, 6)  # 10 + 5 hits AC 13, with a 6 on the 1d8 (+3)
    _action(ui, "Bite").click()
    assert ui.damage_input.text() == "9 Piercing"
    assert "15" in ui._action_result_label.text()
    assert "HIT" in ui._action_result_label.text()
    ui.damage_input.returnPressed.emit()
    assert tiger["hp"] == tiger["max_hp"] - 9


def test_a_miss_leaves_nothing_to_apply(dragon, monkeypatch):
    ui, _, tiger, _ = dragon
    tiger["ac"] = 16
    _dice(monkeypatch, 10, 4)
    _action(ui, "Bite").click()
    assert ui.damage_input.text() == ""
    assert "MISS" in ui._action_result_label.text()


def test_a_natural_20_hits_any_ac_and_doubles_the_dice(dragon, monkeypatch):
    ui, _, tiger, _ = dragon
    tiger["ac"] = 40
    _dice(monkeypatch, 20, 4, 5, 6)
    _action(ui, "Bite").click()
    assert ui.damage_input.text() == "14 Piercing"  # 5 + 6 + 3
    assert "CRITICAL" in ui._action_result_label.text()


def test_a_natural_1_misses_any_ac(dragon, monkeypatch):
    ui, _, tiger, _ = dragon
    tiger["ac"] = 2
    _dice(monkeypatch, 1, 1)
    _action(ui, "Bite").click()
    assert "MISS" in ui._action_result_label.text()


@pytest.mark.parametrize(
    "mode, rolls, total", [("Advantage", (3, 17), 22), ("Disadvantage", (3, 17), 8)]
)
def test_the_roll_mode_counts(dragon, monkeypatch, mode, rolls, total):
    ui, *_ = dragon
    ui.roll_mode_combo.setCurrentText(mode)
    _dice(monkeypatch, *rolls, 1, 1, 1)
    _action(ui, "Bite").click()
    assert f"rolled {total}" in ui._action_result_label.text()


def test_a_players_text_ac_is_read(dragon, monkeypatch):
    ui, _, tiger, _ = dragon
    tiger["ac"] = "18 (with Shield) and 16 (without Shield)"
    _dice(monkeypatch, 12, 4)
    _action(ui, "Bite").click()  # 17 misses the 18
    assert "vs AC 18" in ui._action_result_label.text()
    assert "MISS" in ui._action_result_label.text()


def test_two_damage_types_fill_in_together(dragon, monkeypatch):
    ui, _, tiger, _ = dragon
    tiger["ac"] = 10
    _dice(monkeypatch, 15, 4, 2, 3)
    _action(ui, "Flail").click()
    assert ui.damage_input.text() == "5 Slashing + 3 Fire"
    ui.damage_input.returnPressed.emit()
    assert tiger["hp"] == tiger["max_hp"] - 8


def test_with_several_targets_it_rolls_without_judging_a_hit(dragon, monkeypatch):
    ui, _, _, bandit = dragon
    ui._select_target_character(bandit, ctrl=True)
    _dice(monkeypatch, 15, 4, 2)
    _action(ui, "Bite").click()
    assert ui.damage_input.text() == "5 Piercing"
    label = ui._action_result_label.text()
    assert "HIT" not in label and "MISS" not in label


def test_a_save_ability_says_the_dc_and_is_spent(dragon, monkeypatch):
    ui, pirate, tiger, _ = dragon
    _dice(monkeypatch, 1, 1, 1, 1, 1, 1)
    _action(ui, "Fire Breath").click()
    assert "DC 14 Dexterity save" in ui._action_result_label.text()
    assert ui.damage_input.text() == "6 Fire"
    name = BREATH["name"]
    assert pirate["spent_abilities"] == {name: 1}
    assert not _action(ui, "Fire Breath (Recharge").isEnabled()
    assert f"Pirate uses {name}" in str(
        json.loads(json.dumps(ui._read_log(), cls=LogJSONEncoder))
    )


def test_a_spent_ability_can_be_made_ready(dragon):
    ui, pirate, *_ = dragon
    _action(ui, "Screech").click()
    ui._refresh_views()
    assert not _action(ui, "Screech").isEnabled()
    _action(ui, "↺").click()
    assert pirate["spent_abilities"] == {}
    ui._refresh_views()
    assert _action(ui, "Screech").isEnabled()


def test_using_an_ability_is_one_undo(dragon):
    ui, pirate, *_ = dragon
    _action(ui, "Fire Breath").click()
    ui._undo_last()
    assert not pirate.get("spent_abilities")


def test_legendary_actions_count_down_by_their_cost(dragon, monkeypatch):
    ui, pirate, *_ = dragon
    _action(ui, "Wing Buffet").click()
    assert pirate["legendary_actions_left"] == 1
    assert ui._use_monster_action(pirate, parse_action(WING, legendary=True)) is None
    assert "1 legendary actions left" in _status(ui)
    assert pirate["legendary_actions_left"] == 1
    ui._refresh_views()
    _action(ui, "Lash").click()
    assert pirate["legendary_actions_left"] == 0


def test_legendary_resistance_counts_down(dragon):
    ui, pirate, *_ = dragon
    _action(ui, "Use Legendary Resistance (3 left)").click()
    assert pirate["legendary_resistances_left"] == 2
    ui._refresh_views()
    assert _action(ui, "Use Legendary Resistance (2 left)").isEnabled()
    assert "uses Legendary Resistance (2 left)" in _log_text(ui)
    ui._undo_last()
    assert "legendary_resistances_left" not in pirate


def test_the_card_shows_what_is_left(dragon):
    ui, pirate, *_ = dragon
    pirate["legendary_actions_left"] = 1
    pirate["spent_abilities"] = {"Fire Breath": 1}
    ui._rebuild_card(pirate)
    labels = [
        label.text() for label in ui._card_widgets[id(pirate)].findChildren(QLabel)
    ]
    assert "Legendary 1/3  Resist 3/3" in labels
    assert "Spent: Fire Breath" in labels


def test_a_saved_fights_abilities_still_work(dragon, tmp_path, monkeypatch):
    """Monsters reload from JSON with plain dicts for abilities."""
    ui, pirate, tiger, _ = dragon
    pirate["actions"] = json.loads(json.dumps(pirate["actions"]))
    ui._refresh_views()
    tiger["ac"] = 10
    _dice(monkeypatch, 15, 4, 4)
    _action(ui, "Bite").click()
    assert ui.damage_input.text() == "7 Piercing"


# ---------------------------------------------------------------------------
# 10. Turn-start reminders


def _reminders(ui) -> str:
    return ui._turn_reminders_label.text()


def _to_next_round(ui):
    """Round on to the Pirate's turn again."""
    for _ in range(3):
        ui._advance_turn()


def test_a_dying_player_is_reminded(fight):
    ui, _, tiger, _ = fight
    tiger["_is_player"] = True
    tiger["hp"] = 0
    ui._advance_turn()
    ui._refresh_views()
    assert "Tiger is dying: death save" in _reminders(ui)


def test_legendary_actions_come_back_on_its_turn(dragon):
    ui, pirate, *_ = dragon
    pirate["legendary_actions_left"] = 0
    ui._advance_turn()
    assert pirate["legendary_actions_left"] == 0, "not on someone else's turn"
    ui._advance_turn()
    ui._advance_turn()
    ui._refresh_views()
    assert pirate["legendary_actions_left"] == 3
    assert "Legendary actions back to 3" in _reminders(ui)


def test_nothing_to_regain_isnt_mentioned(dragon):
    ui, *_ = dragon
    _to_next_round(ui)
    ui._refresh_views()
    assert "Legendary" not in _reminders(ui)


def test_a_spent_recharge_rolls_at_the_start_of_its_turn(dragon, monkeypatch):
    ui, pirate, *_ = dragon
    name = BREATH["name"]
    pirate["spent_abilities"] = {name: 1}
    monkeypatch.setattr(random, "randint", lambda low, high: 5)
    _to_next_round(ui)
    ui._refresh_views()
    assert pirate["spent_abilities"] == {}
    assert f"{name} recharged (rolled 5)" in _reminders(ui)
    assert "recharged (rolled 5)" in _log_text(ui)


def test_a_failed_recharge_stays_spent(dragon, monkeypatch):
    ui, pirate, *_ = dragon
    name = BREATH["name"]
    pirate["spent_abilities"] = {name: 1}
    monkeypatch.setattr(random, "randint", lambda low, high: 4)
    _to_next_round(ui)
    ui._refresh_views()
    assert pirate["spent_abilities"] == {name: 1}
    assert f"{name} not recharged (rolled 4)" in _reminders(ui)


def test_a_per_day_ability_doesnt_recharge(dragon, monkeypatch):
    ui, pirate, *_ = dragon
    pirate["spent_abilities"] = {SCREECH["name"]: 1}
    monkeypatch.setattr(random, "randint", lambda low, high: 6)
    _to_next_round(ui)
    assert pirate["spent_abilities"] == {SCREECH["name"]: 1}


def test_start_of_turn_traits_are_reminded(dragon):
    ui, *_ = dragon
    _to_next_round(ui)
    ui._refresh_views()
    assert "Regeneration: It regains 10 Hit Points" in _reminders(ui)


def test_a_reminder_stays_for_the_turn_and_goes_with_it(dragon):
    ui, pirate, *_ = dragon
    _to_next_round(ui)
    ui._refresh_views()
    shown = _reminders(ui)
    assert shown
    ui._refresh_views()
    assert _reminders(ui) == shown
    ui._advance_turn()
    ui._refresh_views()
    assert _reminders(ui) == ""


def test_undoing_a_turn_undoes_its_recharge(dragon, monkeypatch):
    ui, pirate, *_ = dragon
    name = BREATH["name"]
    ui._advance_turn()
    ui._advance_turn()
    pirate["spent_abilities"] = {name: 1}
    monkeypatch.setattr(random, "randint", lambda low, high: 6)
    ui._advance_turn()
    assert pirate["spent_abilities"] == {}
    ui._undo_last()
    assert pirate["spent_abilities"] == {name: 1}


def test_legendary_actions_ready_are_shown_on_others_turns(dragon):
    ui, *_ = dragon
    ui._advance_turn()
    ui._refresh_views()
    assert ui._legendary_ready_label.text() == "Legendary actions ready: Pirate (3)"


def test_a_dead_monster_isnt_ready(dragon):
    ui, pirate, *_ = dragon
    pirate["hp"] = 0
    ui._advance_turn()
    ui._refresh_views()
    assert ui._legendary_ready_label.text() == ""


# ---------------------------------------------------------------------------
# 11. Faster initiative


@pytest.fixture
def setup(tmp_path):
    """Before the fight: a player (the Tiger) and two monsters."""
    ui = make_ui(tmp_path, [Pirate(), Tiger(), _named(Pirate(), "Bandit")])
    pirate, tiger, bandit = ui.characters
    tiger["_is_player"] = True
    return ui, pirate, tiger, bandit


def _field(ui, char):
    return ui._initiative_inputs[id(char)]


def test_roll_for_monsters_leaves_the_players_to_their_dice(setup):
    ui, pirate, tiger, bandit = setup
    _button(ui._window, "Roll for Monsters").click()
    assert _field(ui, pirate).text() and _field(ui, bandit).text()
    assert _field(ui, tiger).text() == ""


def test_roll_for_monsters_keeps_what_is_typed(setup):
    ui, pirate, *_ = setup
    _field(ui, pirate).setText("3")
    _button(ui._window, "Roll for Monsters").click()
    assert _field(ui, pirate).text() == "3"


def test_enter_moves_to_the_next_empty_field(setup, monkeypatch):
    ui, pirate, tiger, bandit = setup
    focused = []
    for char in (pirate, tiger, bandit):
        monkeypatch.setattr(
            _field(ui, char), "setFocus", lambda c=char: focused.append(c)
        )
    _field(ui, pirate).setText("12")
    _field(ui, pirate).returnPressed.emit()
    assert focused == [tiger]


def test_enter_on_a_field_that_isnt_a_number_stays_on_it(setup, monkeypatch):
    ui, pirate, tiger, bandit = setup
    _field(ui, pirate).setText("abc")
    focused = []
    monkeypatch.setattr(_field(ui, pirate), "setFocus", lambda: focused.append(pirate))
    _field(ui, pirate).returnPressed.emit()
    assert focused == [pirate]
    assert ui.phase == "INITIATIVE"


def test_enter_starts_the_fight_once_all_are_filled_in(setup):
    ui, pirate, tiger, bandit = setup
    for value, char in enumerate((pirate, tiger, bandit), start=10):
        _field(ui, char).setText(str(value))
    _field(ui, bandit).returnPressed.emit()
    assert ui.phase == "COMBAT"


def test_ties_can_go_by_dexterity_with_no_dialog(setup):
    ui, pirate, tiger, bandit = setup
    pirate["Ability Scores"] = {"DEX": 10}
    tiger["Ability Scores"] = {"DEX": 18}
    bandit["Ability Scores"] = {"DEX": 14}
    ui.settings.ask_initiative_ties = False
    _start(ui, 12, 12, 12)  # the fixture fails on a dialog
    assert ui.initiative_order == [tiger, bandit, pirate]


# ---------------------------------------------------------------------------
# 12. Up next, and the players' screen


def test_now_and_next(fight):
    ui, *_ = fight
    ui._refresh_views()
    assert ui._turn_now_label.text() == "Now: Pirate"
    assert ui._turn_next_label.text() == "Next: Tiger, then Bandit (Pirate)"


def test_next_wraps_round_and_leaves_out_the_dead(fight):
    ui, _, tiger, _ = fight
    tiger["hp"] = 0
    ui._advance_turn()
    ui._refresh_views()
    assert ui._turn_now_label.text() == "Now: Bandit (Pirate)"
    assert ui._turn_next_label.text() == "Next: Pirate"


def _rows(ui):
    return player_view_rows(
        ui.initiative_order,
        ui._current_turn_group(),
        ui._upcoming_turns(),
        ui._char_death_state,
    )


def test_monsters_show_a_word_not_their_hit_points(fight):
    ui, pirate, tiger, bandit = fight
    tiger["hp"] = 15
    bandit["hp"] = 0
    rows = {row.name: row for row in _rows(ui)}
    assert rows["Tiger"].health == "Bloodied"
    assert rows["Pirate"].health == "Healthy"
    assert rows["Bandit (Pirate)"].health == "Defeated"
    assert "15" not in str(rows["Tiger"])


def test_a_players_numbers_are_shown(fight):
    ui, _, tiger, _ = fight
    tiger.update(_is_player=True, hp=12, max_hp=30, temp_hp=4)
    assert next(r for r in _rows(ui) if r.name == "Tiger").health == "12 / 30 (+4)"


def test_a_dying_player_shows_their_saves(fight):
    ui, _, tiger, _ = fight
    tiger.update(_is_player=True, hp=0, death_saves_fail=1, death_saves_success=2)
    row = next(r for r in _rows(ui) if r.name == "Tiger")
    assert row.health == "Dying (1 failed, 2 saved)"


def test_now_and_next_are_marked(fight):
    ui, *_ = fight
    assert [row.turn for row in _rows(ui)] == ["now", "next", ""]


@pytest.mark.parametrize("key", ["conditions", "visibility_states"])
def test_a_monster_they_cant_perceive_isnt_listed(fight, key):
    ui, _, tiger, _ = fight
    tiger[key] = ["Invisible"]
    rows = _rows(ui)
    assert "Tiger" not in [row.name for row in rows]
    assert [row.turn for row in rows] == ["now", "next"], "Next isn't a giveaway"


def test_an_invisible_player_is_still_listed(fight):
    ui, _, tiger, _ = fight
    tiger.update(_is_player=True, conditions=["Invisible"])
    assert "Tiger" in [row.name for row in _rows(ui)]


def test_what_a_monster_is_doing_inside_stays_hidden(fight):
    ui, _, tiger, _ = fight
    tiger["conditions"] = ["Prone", "Concentrating", "Bloodied"]
    row = next(r for r in _rows(ui) if r.name == "Tiger")
    assert row.conditions == ("Prone",)


def test_a_group_counts_its_health_and_hides_a_member_they_cant_see(tmp_path):
    ui = make_ui(
        tmp_path,
        [
            _named(Tiger(), "Tiger 1", "Tigers"),
            _named(Tiger(), "Tiger 2", "Tigers"),
            _named(Tiger(), "Tiger 3", "Tigers"),
        ],
    )
    ui._initiative_inputs[id(ui.characters[0])].setText("9")
    ui._start_combat()
    one, two, three = ui.characters
    one["hp"] = 5
    three["conditions"].append("Invisible")
    (row,) = _rows(ui)
    assert row.name == "Tigers (2)"
    assert row.health == "1 Bloodied, 1 Healthy"


def _view_text(ui) -> str:
    view = ui._player_view
    return " ".join(label.text() for label in view.findChildren(QLabel))


def test_the_players_screen_opens_follows_and_closes(fight):
    ui, *_ = fight
    _button(ui._window, "Player Screen").click()
    assert ui._player_view is not None and ui._player_view.isVisible()
    assert "Round 1" in _view_text(ui)
    ui._advance_turn()
    ui._advance_turn()
    ui._advance_turn()
    ui._refresh_views()
    assert "Round 2" in _view_text(ui)
    _button(ui._window, "Player Screen").click()
    assert ui._player_view is None


def test_a_change_reaches_the_screen_by_itself(fight):
    ui, _, tiger, _ = fight
    _button(ui._window, "Player Screen").click()
    tiger["hp"] = 5
    ui._rebuild_card(tiger)
    assert ui._views_timer.isActive()
    QApplication.processEvents()
    assert "Bloodied" in _view_text(ui)
    ui._toggle_player_view()


def test_before_the_fight_the_screen_waits(tmp_path):
    ui = make_ui(tmp_path, [Pirate()])
    ui._toggle_player_view()
    assert "Waiting for the fight" in _view_text(ui)
    ui._toggle_player_view()


# ---------------------------------------------------------------------------
# 13. A tidier panel, and a card's quick menu


def test_rarely_used_controls_are_collapsed(fight):
    ui, *_ = fight
    assert not ui._more_controls.isVisibleTo(ui._window)
    ui._more_controls_btn.click()
    assert ui._more_controls.isVisibleTo(ui._window)
    assert ui.settings.show_more_controls is True
    ui._more_controls_btn.click()
    assert not ui._more_controls.isVisibleTo(ui._window)


def test_the_settings_dialog_shows_them_too(fight, monkeypatch):
    ui, *_ = fight
    dlg = open_dialog(monkeypatch, ui._show_settings_dialog)
    box = dlg.findChild(QCheckBox, "show_more_controls")
    box.setChecked(True)
    assert ui._more_controls.isVisibleTo(ui._window)


def test_shortcuts_keep_working_while_collapsed(fight):
    ui, pirate, *_ = fight
    pirate["spell_slots"] = {1: 1}
    ui._select_character(pirate)
    ui._spell_slot_shortcuts[0].activated.emit()
    assert pirate["spell_slots"] == {1: 0}


def test_every_setting_has_words(fight):
    for _, infos in SETTING_SECTIONS:
        for info in infos:
            assert info.label and info.hint


def _menu_actions(menu) -> dict:
    return {a.text(): a for a in menu.actions() if a.text()}


def test_right_clicking_the_only_target_opens_the_menu(fight, monkeypatch):
    ui, pirate, tiger, _ = fight
    opened = []
    monkeypatch.setattr(ui, "_card_menu", lambda char: opened.append(char) or _Menu())
    ui._card_right_clicked(pirate, False, False)
    assert ui.target_characters == [pirate] and opened == [], "a new target"
    ui._card_right_clicked(pirate, False, False)
    assert opened == [pirate]


class _Menu:
    def popup(self, _pos):
        pass


@pytest.mark.parametrize("ctrl, shift", [(True, False), (False, True)])
def test_ctrl_and_shift_never_open_it(fight, monkeypatch, ctrl, shift):
    ui, _, tiger, _ = fight
    opened = []
    monkeypatch.setattr(ui, "_card_menu", lambda char: opened.append(char) or _Menu())
    ui._card_right_clicked(tiger, ctrl, shift)
    assert opened == []


def test_a_menu_condition_is_one_click_each_way(fight):
    ui, pirate, tiger, _ = fight
    actions = _menu_actions(ui._card_menu(tiger))
    assert not actions["Prone"].isChecked()
    actions["Prone"].trigger()
    assert "Prone" in tiger["conditions"]
    assert "Tiger gains Prone from Pirate" in _log_text(ui)

    actions = _menu_actions(ui._card_menu(tiger))
    assert actions["Prone"].isChecked()
    actions["Prone"].trigger()
    assert "Prone" not in tiger["conditions"]


def test_the_menu_goes_to_the_amount_fields(fight, monkeypatch):
    ui, _, tiger, _ = fight
    focused = []
    monkeypatch.setattr(ui.heal_input, "setFocus", lambda: focused.append("heal"))
    _menu_actions(ui._card_menu(tiger))["Heal (H)"].trigger()
    assert focused == ["heal"]


# ---------------------------------------------------------------------------
# And fewer clicks and popups all round


def test_turn_panel_only_shows_in_combat(tmp_path):
    ui = make_ui(tmp_path, [Pirate()])
    assert not ui._turn_panel.isVisibleTo(ui._window)
    _start(ui, 5)
    assert ui._turn_panel.isVisibleTo(ui._window)


@pytest.mark.parametrize("key", ["S", "F", "I"])
def test_the_source_dialogs_have_shortcuts(fight, key):
    ui, *_ = fight
    shortcut = {
        "S": ui._cast_spell_shortcut,
        "F": ui._enable_feature_shortcut,
        "I": ui._more_info_shortcut,
    }[key]
    assert shortcut in ui._combo_sensitive_shortcuts
    assert shortcut.key().toString() == key


@pytest.mark.parametrize(
    "open_it",
    [
        lambda ui: ui._show_cast_spell_dialog(),
        lambda ui: ui._show_enable_feature_dialog(),
        lambda ui: ui._show_more_info(),
    ],
)
def test_no_source_says_so_instead_of_nothing(fight, open_it):
    ui, *_ = fight
    ui._clear_selection()
    open_it(ui)
    assert "pick a source" in _status(ui)


def test_no_target_for_a_spell_or_condition_is_no_popup(fight):
    ui, pirate, *_ = fight
    ui._set_targets([])
    ui._apply_cast_spell(SpellFactory.create("Hold Person"))
    assert "needs a target" in _status(ui)
    ui._show_custom_condition_dialog()
    assert "pick a target" in _status(ui)


def test_escape_leaves_a_field_before_it_clears_anything(fight, monkeypatch):
    ui, pirate, tiger, _ = fight
    monkeypatch.setattr(QApplication, "focusWidget", lambda: ui.damage_input)
    ui._escape_pressed()
    assert ui.selected_character is pirate and ui.target_characters == [tiger]

    monkeypatch.setattr(QApplication, "focusWidget", lambda: None)
    ui._escape_pressed()
    assert ui.selected_character is None and ui.target_characters == []


def test_jumping_to_damage_after_a_target_is_a_setting(fight, monkeypatch):
    ui, pirate, *_ = fight
    focused = []
    monkeypatch.setattr(ui.damage_input, "setFocus", lambda: focused.append(1))
    ui._select_target_character(pirate)
    assert focused == []
    ui.settings.focus_damage_on_target = True
    ui._select_target_character(pirate)
    assert focused == [1]


def _spell_tree(dlg):
    return dlg.findChild(QTreeWidget)


def _search_box(dlg):
    return dlg.findChild(QLineEdit)


def test_enter_in_the_spell_search_picks_then_casts(fight, monkeypatch):
    ui, pirate, tiger, _ = fight
    pirate["spell_slots"] = {2: 1}
    dlg = open_dialog(monkeypatch, ui._show_cast_spell_dialog)
    search = _search_box(dlg)
    search.setText("hold person")
    search.returnPressed.emit()
    assert _spell_tree(dlg).currentItem().text(0) == "Hold Person"
    assert "Hold Person" not in tiger["conditions"], "the first Enter only picks"
    search.returnPressed.emit()
    assert "Hold Person" in tiger["conditions"]
    assert pirate["spell_slots"] == {2: 0}


def test_double_clicking_a_spell_casts_it(fight, monkeypatch):
    ui, _, tiger, _ = fight
    dlg = open_dialog(monkeypatch, ui._show_cast_spell_dialog)
    search = _search_box(dlg)
    search.setText("hold person")
    search.returnPressed.emit()
    tree = _spell_tree(dlg)
    tree.itemActivated.emit(tree.currentItem(), 0)
    assert "Hold Person" in tiger["conditions"]


def test_enter_isnt_the_dialogs_default_button(fight, monkeypatch):
    ui, *_ = fight
    dlg = open_dialog(monkeypatch, ui._show_cast_spell_dialog)
    assert not any(b.autoDefault() for b in dlg.findChildren(QPushButton))


# ---------------------------------------------------------------------------
# What the review of the first round of fixes found


def test_a_monster_reloaded_from_a_log_can_cast(tmp_path, monkeypatch):
    """A log's JSON makes spell slot levels strings: without turning them back
    the Cast Spell dialog raised, and that ended the app."""
    ui = make_ui(tmp_path, [Pirate()])
    (pirate,) = ui.characters
    pirate["spell_slots"] = {1: 3, 2: 2}
    _start(ui, 5)
    ui._select_character(pirate)
    ui._add_action_use("Action")  # so the log has a fight to continue
    log = ui.log_file

    fresh = make_ui(tmp_path, [])
    fresh._load_log_from_path(str(log))
    (loaded,) = fresh.characters
    assert loaded["spell_slots"] == {1: 3, 2: 2}
    fresh._select_character(loaded)
    fresh._cast_spell_slot_level(1)
    assert loaded["spell_slots"] == {1: 2, 2: 2}
    dlg = open_dialog(monkeypatch, fresh._show_cast_spell_dialog)
    search = _search_box(dlg)
    search.setText("hold person")
    search.returnPressed.emit()
    assert _spell_tree(dlg).currentItem().text(0) == "Hold Person"


def test_a_players_resistance_counts(tmp_path):
    """Obmar's Dwarven Resilience: resistances never reached the combat dict,
    so Apply took a player's damage in full."""
    ui = make_ui(tmp_path, [], [Obmar().build()])
    (obmar,) = ui.characters
    _start(ui, 10)
    ui._select_target_character(obmar)
    hp = obmar["hp"]
    _damage_field(ui, "10 poison")
    assert obmar["hp"] == hp - 5
    assert "(resisted)" in _log_text(ui)


def _all_dead_with_a_group(tmp_path):
    ui = make_ui(
        tmp_path,
        [
            Pirate(),
            *(_named(Tiger(), f"Tiger {n}", "Tigers") for n in range(1, 7)),
        ],
    )
    pirate, *tigers = ui.characters
    ui._initiative_inputs[id(pirate)].setText("15")
    ui._initiative_inputs[id(tigers[0])].setText("10")
    ui._start_combat()
    for char in ui.characters:
        char["hp"] = 0
    return ui


def test_next_laps_once_in_turns_not_combatants(tmp_path):
    ui = _all_dead_with_a_group(tmp_path)
    ui._advance_turn()
    assert ui.round_number == 2


def test_previous_laps_once_too(tmp_path):
    ui = _all_dead_with_a_group(tmp_path)
    ui.round_number = 6
    ui._add_action_use("Action")
    ui._previous_turn()
    assert ui.round_number == 5


def test_next_says_round_when_only_the_dead_are_left_this_round(fight):
    ui, _, _, bandit = fight
    bandit["hp"] = 0
    ui._advance_turn()  # the Tiger's turn, and only the dead Bandit after it
    assert ui._next_turn_btn.text() == "Next Round"


def test_next_changes_its_mind_when_someone_dies(fight):
    ui, _, _, bandit = fight
    ui._advance_turn()
    assert ui._next_turn_btn.text() == "Next Combatant"
    bandit["hp"] = 0
    ui._refresh_views()
    assert ui._next_turn_btn.text() == "Next Round"


def test_healing_the_dead_says_so(fight):
    ui, _, tiger, _ = fight
    tiger["hp"] = 0
    ui.heal_input.setText("5")
    ui._apply_heal()
    assert "Tiger is dead" in _status(ui)
    assert ui.heal_input.text() == "5"
    assert tiger["hp"] == 0


def test_healing_the_living_among_the_dead_says_who_wasnt(fight):
    ui, _, tiger, bandit = fight
    bandit["hp"] = 5
    tiger["hp"] = 0
    ui._select_target_character(bandit, ctrl=True)
    ui.heal_input.setText("5")
    ui._apply_heal()
    assert bandit["hp"] == 10
    assert "Tiger is dead" in _status(ui)


@pytest.mark.parametrize(
    "act, words",
    [
        (lambda ui: ui._remove_action_use("Action"), "no Action logged"),
        (lambda ui: ui._remove_condition(), "no target has"),
        (lambda ui: ui._undo_last(), "Nothing to undo"),
    ],
)
def test_the_last_quiet_paths_speak(fight, act, words):
    ui, *_ = fight
    ui.history = []
    act(ui)
    assert words in _status(ui)


@pytest.mark.parametrize(
    "act, words",
    [
        (lambda ui: ui._shortcut_add_concentration(), "pick a source"),
        (lambda ui: ui._shortcut_remove_concentration(), "pick a source"),
        (lambda ui: ui._shortcut_clear_target_conditions(), "pick a target"),
    ],
)
def test_the_concentration_keys_speak_too(fight, act, words):
    ui, *_ = fight
    ui._clear_selection()
    act(ui)
    assert words in _status(ui)


def test_an_error_in_a_click_is_said_not_fatal(fight, capsys):
    ui, *_ = fight
    try:
        raise TypeError("a bug")
    except TypeError as error:
        ui._report_uncaught_error(TypeError, error, error.__traceback__)
    assert "TypeError" in _status(ui) and "a bug" in _status(ui)
    assert "a bug" in capsys.readouterr().err


def test_a_spell_ended_by_a_new_cast_isnt_logged_as_a_cast(fight):
    ui, pirate, *_ = fight
    ui._apply_cast_spell(SpellFactory.create("Hold Person"))
    ui._apply_cast_spell(SpellFactory.create("Hold Person"))
    ended = [
        event
        for event in ui._read_log()["round_1"]
        if "concentration broken" in event["text"]
    ]
    assert len(ended) == 1
    assert "action" not in ended[0]


def test_replay_ignores_the_ended_spells_older_logs_marked_as_casts(fight):
    ui, pirate, *_ = fight
    before = dict(pirate["stats"]["spells_cast_by_name"])
    spells_cast = pirate["stats"]["spells_cast"]
    ui._apply_replay_action(pirate, Action.CAST_SPELL, None)
    assert pirate["stats"]["spells_cast"] == spells_cast
    assert pirate["stats"]["spells_cast_by_name"] == before


# ---------------------------------------------------------------------------
# What the review of items 6-13 found. Keys are real keystrokes here: a test
# calling the handler can't see a shortcut taking the key first.


@pytest.fixture
def shown_fight(fight):
    ui, pirate, tiger, bandit = fight
    ui._window.show()
    ui._window.activateWindow()
    QApplication.processEvents()
    yield ui, pirate, tiger, bandit
    ui._window.close()


def _type_into(field, text: str):
    field.setFocus()
    QApplication.processEvents()
    QTest.keyClicks(field, text)


def test_enter_in_the_damage_field_applies_it_and_keeps_the_turn(shown_fight):
    ui, pirate, tiger, _ = shown_fight
    _type_into(ui.damage_input, "3 fi")
    QTest.keyClick(ui.damage_input, Qt.Key.Key_Return)
    assert tiger["hp"] == tiger["max_hp"] - 3
    assert ui.initiative_order[ui.current_turn_idx] is pirate


def test_enter_in_the_heal_field_applies_it(shown_fight):
    ui, _, tiger, _ = shown_fight
    tiger["hp"] = 10
    _type_into(ui.heal_input, "4")
    QTest.keyClick(ui.heal_input, Qt.Key.Key_Return)
    assert tiger["hp"] == 14


def test_enter_is_next_turn_again_after_esc(shown_fight):
    ui, _, tiger, _ = shown_fight
    _type_into(ui.damage_input, "3 fi")
    QTest.keyClick(ui.damage_input, Qt.Key.Key_Return)
    QTest.keyClick(ui.damage_input, Qt.Key.Key_Escape)
    QApplication.processEvents()
    QTest.keyClick(ui._window, Qt.Key.Key_Return)
    assert ui.initiative_order[ui.current_turn_idx] is tiger


def test_enter_walks_the_initiative_fields_and_starts_the_fight(setup):
    ui, pirate, tiger, bandit = setup
    ui._window.show()
    ui._window.activateWindow()
    QApplication.processEvents()
    for value, char in zip(("15", "10", "5"), (pirate, tiger, bandit)):
        field = _field(ui, char)
        _type_into(field, value)
        QTest.keyClick(field, Qt.Key.Key_Return)
    assert ui.phase == "COMBAT"
    ui._window.close()


def test_ctrl_z_undoes_with_the_cursor_in_the_damage_field(shown_fight):
    ui, pirate, _, _ = shown_fight
    pirate.update(actions=[BREATH])
    ui._refresh_views()
    QApplication.processEvents()  # a new button shows on the next event cycle
    _action(ui, "Fire Breath").click()
    assert pirate["spent_abilities"]
    _type_into(ui.damage_input, "")
    QTest.keyClick(ui.damage_input, Qt.Key.Key_Z, Qt.KeyboardModifier.ControlModifier)
    assert not pirate.get("spent_abilities")
    assert ui.damage_input.text() == ""


GOBLIN_SCIMITAR = {
    "name": "Scimitar",
    "description": "Melee Attack Roll: +4, reach 5 ft. Hit: 5 (1d6 + 2) Slashing"
    " damage, plus 2 (1d4) Slashing damage if the attack roll had Advantage.",
}


def test_damage_that_depends_on_something_isnt_rolled_in(dragon, monkeypatch):
    ui, pirate, tiger, _ = dragon
    pirate["actions"] = [GOBLIN_SCIMITAR]
    tiger["ac"] = 10
    ui._refresh_views()
    _dice(monkeypatch, 15, 4, 3)
    _action(ui, "Scimitar").click()
    assert ui.damage_input.text() == "5 Slashing"
    assert "Also: plus 2 (1d4) Slashing damage if the attack roll had Advantage" in (
        ui._action_result_label.text()
    )


def test_a_miss_says_nothing_of_what_a_hit_would_do(dragon, monkeypatch):
    ui, pirate, tiger, _ = dragon
    pirate["actions"] = [GOBLIN_SCIMITAR]
    tiger["ac"] = 30
    ui._refresh_views()
    _dice(monkeypatch, 5, 1)
    _action(ui, "Scimitar").click()
    assert "Also" not in ui._action_result_label.text()


def test_the_result_never_moves_the_buttons(dragon):
    ui, *_ = dragon
    label = ui._action_result_label
    assert label.minimumHeight() == label.maximumHeight() > 0


def test_a_type_of_its_choice_is_never_guessed(dragon, monkeypatch):
    ui, pirate, tiger, _ = dragon
    pirate["actions"] = [
        {
            "name": "Claw",
            "description": "Melee Attack Roll: +5, reach 5 ft. Hit: 4 (1d4 + 2)"
            " Slashing damage plus 7 (2d6) damage of a type it chooses.",
        }
    ]
    tiger["ac"] = 10
    ui._refresh_views()
    _dice(monkeypatch, 15, 4, 2, 3, 4)
    _action(ui, "Claw").click()
    assert ui.damage_input.text() == "4 Slashing + 7 type"
    assert ui.damage_input.selectedText() == "type"

    ui.damage_input.returnPressed.emit()
    assert tiger["hp"] == tiger["max_hp"], "Enter waits for the type"
    assert "isn't a damage type" in _status(ui)

    ui.damage_input.setText("4 Slashing + 7 fi")
    ui.damage_input.returnPressed.emit()
    assert tiger["hp"] == tiger["max_hp"] - 11


@pytest.mark.parametrize(
    "condition",
    ["Invisibility", "Greater Invisibility", "Total Cover", "Darkness", "Hidden"],
)
def test_more_ways_of_being_unseen(fight, condition):
    ui, _, tiger, _ = fight
    tiger["conditions"] = [condition]
    assert "Tiger" not in [row.name for row in _rows(ui)]


def test_spell_badges_and_custom_conditions_stay_private(fight):
    ui, _, tiger, _ = fight
    tiger["conditions"] = ["Prone", "Secretly the Lich's spy", "Bane"]
    assert next(r for r in _rows(ui) if r.name == "Tiger").conditions == ("Prone",)


def test_a_players_own_conditions_all_show(fight):
    ui, _, tiger, _ = fight
    tiger.update(_is_player=True, conditions=["Bane", "Concentrating"])
    row = next(r for r in _rows(ui) if r.name == "Tiger")
    assert row.conditions == ("Bane", "Concentrating")


def test_an_unseen_monsters_turn_doesnt_move_now(fight):
    ui, _, tiger, _ = fight
    tiger["conditions"] = ["Invisible"]
    ui._advance_turn()  # the unseen Tiger's turn
    assert [(row.name, row.turn) for row in _rows(ui)] == [
        ("Pirate", "now"),
        ("Bandit (Pirate)", "next"),
    ]


def test_undoing_a_saved_hit_keeps_it_saved(fight):
    ui, _, tiger, _ = fight
    ui._half_btn.click()
    _damage_field(ui, "20 fi")
    assert tiger["hp"] == tiger["max_hp"] - 10
    ui._undo_last()
    assert ui._half_btn.isChecked()
    assert ui.damage_input.text() == "20 fi"
    ui.damage_input.returnPressed.emit()
    assert tiger["hp"] == tiger["max_hp"] - 10


def test_undoing_a_rolled_action_takes_its_damage_back(dragon, monkeypatch):
    ui, _, tiger, _ = dragon
    _dice(monkeypatch, *[1] * 6)
    _action(ui, "Fire Breath").click()
    assert ui.damage_input.text() == "6 Fire"
    ui._undo_last()
    assert ui.damage_input.text() == ""
    assert ui._action_result_label.text() == ""


def test_a_roll_left_unapplied_doesnt_cross_into_the_next_turn(dragon, monkeypatch):
    ui, *_ = dragon
    _dice(monkeypatch, *[1] * 6)
    _action(ui, "Fire Breath").click()
    ui._advance_turn()
    assert ui.damage_input.text() == ""


def test_an_amount_typed_by_hand_stays_across_a_turn(fight):
    ui, *_ = fight
    ui.damage_input.setText("12")
    ui._advance_turn()
    assert ui.damage_input.text() == "12"


def test_picking_a_source_leaves_the_type_of_an_amount_typed(fight):
    ui, _, tiger, bandit = fight
    ui.damage_input.setText("12 fi")
    ui._select_character(bandit)
    assert ui.damage_type_combo.currentData() == FIRE


def test_saved_doesnt_outlast_the_turn(fight):
    ui, _, tiger, _ = fight
    ui.settings.clear_targets_on_turn = False
    ui._half_btn.click()
    ui._advance_turn()
    assert not ui._half_btn.isChecked()
    assert ui._saved_targets == []
    assert ui.target_characters == [tiger]


def test_a_players_owed_save_comes_back_with_the_fight(tmp_path):
    ui = make_ui(tmp_path, [Pirate()], [Obmar().build()])
    obmar, pirate = ui.characters
    _start(ui, 10, 5)
    ui._select_character(pirate)
    ui._select_target_character(obmar)
    obmar["conditions"].append("Concentrating")
    _damage_field(ui, "4 fi")
    assert obmar["concentration_checks"] == [10]

    fresh = make_ui(tmp_path, [], [Obmar().build()])
    fresh._load_log_from_path(str(ui.log_file))
    loaded = next(c for c in fresh.characters if c.get("_is_player"))
    assert loaded["concentration_checks"] == [10]


def test_a_settled_save_doesnt_come_back(tmp_path):
    ui = make_ui(tmp_path, [Pirate()], [Obmar().build()])
    obmar, pirate = ui.characters
    _start(ui, 10, 5)
    ui._select_character(pirate)
    ui._select_target_character(obmar)
    obmar["conditions"].append("Concentrating")
    _damage_field(ui, "4 fi")
    ui._settle_concentration(obmar, 10, kept=True)
    assert PLAYER_SAVES_KEY not in ui._read_log()


def test_a_new_concentration_spell_clears_the_old_save(fight):
    ui, pirate, _, _ = fight
    ui._apply_cast_spell(SpellFactory.create("Hold Person"))
    pirate["concentration_checks"] = [10]
    ui._apply_cast_spell(SpellFactory.create("Hold Person"))
    assert "concentration_checks" not in pirate


def test_giving_a_use_back_is_one_use(dragon):
    ui, pirate, *_ = dragon
    action = parse_action({"name": "Curse (3/Day)", "description": "text"})
    pirate["spent_abilities"] = {"Curse (3/Day)": 2}
    ui._restore_ability(pirate, action)
    assert pirate["spent_abilities"] == {"Curse (3/Day)": 1}


def test_closing_the_players_screen_with_its_x_forgets_it(fight):
    ui, *_ = fight
    ui._toggle_player_view()
    view = ui._player_view
    view.close()
    assert ui._player_view is None
    ui._toggle_player_view()
    assert ui._player_view is not view
    ui._toggle_player_view()


def test_the_players_screen_doesnt_keep_the_app_open(fight):
    ui, *_ = fight
    ui._toggle_player_view()
    assert not ui._player_view.testAttribute(Qt.WidgetAttribute.WA_QuitOnClose)
    ui._toggle_player_view()


def test_esc_closes_the_players_screen(fight):
    ui, *_ = fight
    ui._toggle_player_view()
    QTest.keyClick(ui._player_view, Qt.Key.Key_Escape)
    assert ui._player_view is None


def test_a_recharge_gets_one_roll_a_turn(dragon, monkeypatch):
    ui, pirate, *_ = dragon
    name = BREATH["name"]
    ui._advance_turn()
    ui._advance_turn()
    pirate["spent_abilities"] = {name: 1}
    rolls = iter([2, 6])
    monkeypatch.setattr(random, "randint", lambda low, high: next(rolls))
    ui._advance_turn()  # a 2: it stays spent
    ui._undo_last()
    ui._advance_turn()  # the same 2, not the 6
    assert pirate["spent_abilities"] == {name: 1}
