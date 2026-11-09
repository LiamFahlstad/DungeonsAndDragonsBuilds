"""The rules conditions counting in the rolls the combat UI makes (plan step
3.2, Combat/Effects): attack rolls against and by a combatant with a
condition, the hit and the log that say so, and the reminders the Custom
dialog shows for rolls made at the table. Expected values come from the Rules
Glossary's Blinded, Paralyzed, Poisoned, Prone and Restrained entries, and
Cover."""

import random

import pytest
from PyQt6.QtWidgets import QDialog, QLabel, QMessageBox, QPushButton, QWidget

from Combat.Combatants import Pirate, Tiger
from Combat.CombatUIQt.monster_actions import MonsterAction
from Combat.CombatUIQt.public_log import _ATTACK
from Combat.CombatUIQt.saves import ATTACK_ROLL, CustomEffect
from Core.Definitions import Condition, DamageType
from Model.Content import RulesConditions
from Model.Content.CombatModifiers import ArmorClass
from Model.Creatures.Combatants import Visibility
from tests._combat_ui import make_ui, open_dialog

FIRE = DamageType.FIRE.value
# +5 against AC 15: a 10 hits, a 9 misses.
BOLT = {"damage": [(20, FIRE)], "attack_bonus": 5, "name": "Fire Bolt"}


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)


@pytest.fixture
def fight(tmp_path):
    """A Pirate (the source) attacking a Tiger at AC 15."""
    ui = make_ui(tmp_path, [Pirate(), Tiger()])
    pirate, tiger = ui.characters
    for char, value in zip(ui.characters, (15, 10)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    ui._select_target_character(tiger)
    tiger["ac"] = 15
    tiger["Saving Throws"] = {"DEX": 3}
    return ui, pirate, tiger


def _d20s(monkeypatch, *pairs: tuple[int, int]):
    """random.randint gives these pairs: the two d20s a roll always throws."""
    results = iter(value for pair in pairs for value in pair)
    monkeypatch.setattr(random, "randint", lambda low, high: next(results))


def _log(ui) -> str:
    return str(ui._read_log())


def test_an_attack_on_a_restrained_target_has_advantage(fight, monkeypatch):
    """ "Attack rolls against you have Advantage": of 4 and 12, the 12 counts."""
    ui, _, tiger = fight
    tiger["conditions"].append("Restrained")
    _d20s(monkeypatch, (4, 12))
    ui._apply_custom_effect(CustomEffect(**BOLT))
    assert tiger["hp"] == tiger["max_hp"] - 20
    assert (
        "Pirate's attack roll of 17 hits Tiger, Tiger is Restrained: Advantage"
        in _log(ui)
    )


def test_a_blinded_attacker_has_disadvantage(fight, monkeypatch):
    """Blinded: "your attack rolls have Disadvantage": of 12 and 4, the 4."""
    ui, pirate, tiger = fight
    pirate["conditions"].append("Blinded")
    _d20s(monkeypatch, (12, 4))
    ui._apply_custom_effect(CustomEffect(**BOLT))
    assert tiger["hp"] == tiger["max_hp"]
    assert "Pirate is Blinded: Disadvantage" in _log(ui)


def test_a_poisoned_attacker_against_a_paralyzed_target_rolls_one_d20(
    fight, monkeypatch
):
    """Poisoned's Disadvantage and Paralyzed's Advantage cancel out: the first
    d20 counts."""
    ui, pirate, tiger = fight
    pirate["conditions"].append("Poisoned")
    tiger["conditions"].append("Paralyzed")
    _d20s(monkeypatch, (12, 4))
    ui._apply_custom_effect(CustomEffect(**BOLT))
    assert tiger["hp"] == tiger["max_hp"] - 20
    assert "Advantage and Disadvantage cancel out" in _log(ui)


def test_a_hit_on_a_paralyzed_target_says_to_check_for_a_critical_hit(
    fight, monkeypatch
):
    """ "Any attack roll that hits you is a Critical Hit if the attacker is
    within 5 feet of you": the simulator doesn't know, so the GM is told."""
    ui, _, tiger = fight
    tiger["conditions"].append("Paralyzed")
    _d20s(monkeypatch, (12, 4))
    ui._apply_custom_effect(CustomEffect(**BOLT))
    assert "Tiger is Paralyzed: a Critical Hit if the attacker is within 5" in _log(ui)


def test_a_typed_attack_roll_is_used_as_it_is_and_only_gets_the_hit_note(fight):
    ui, _, tiger = fight
    tiger["conditions"].append("Paralyzed")
    ui.attack_roll_input.setText("15")
    ui._apply_attack_roll()
    lines = [line for line in _log(ui).split("', '") if "attack roll of 15" in line]
    assert len(lines) == 1, lines
    assert "Advantage" not in lines[0]
    assert "a Critical Hit if the attacker is within 5 feet" in lines[0]


def test_a_prone_target_changes_nothing_and_says_why(fight, monkeypatch):
    ui, _, tiger = fight
    tiger["conditions"].append("Prone")
    _d20s(monkeypatch, (12, 4))
    ui._apply_custom_effect(CustomEffect(**BOLT))
    assert tiger["hp"] == tiger["max_hp"] - 20  # the first d20, 12
    assert "Tiger is Prone (not counted): Advantage if the attacker" in _log(ui)


def test_an_attack_line_with_notes_still_reads_on_the_player_link():
    text = (
        "Pirate's attack roll of natural 20 hits Tiger (critical hit),"
        " Tiger is Restrained: Advantage"
    )
    match = _ATTACK.fullmatch(text)
    assert match is not None
    assert match.groups() == (
        "Pirate",
        "natural 20",
        "hits",
        "Tiger",
        " (critical hit)",
    )


def test_ac_counts_its_modifiers(fight, monkeypatch):
    """A modifier's AC bonus counts against the roll (no rules condition has
    one; Shield of Faith will, step 3.3): 15 + 2 is missed by a 15."""
    ui, _, tiger = fight
    monkeypatch.setitem(
        RulesConditions.CONDITION_RULES, Condition.DEAFENED, (ArmorClass(2),)
    )
    tiger["conditions"].append("Deafened")
    _d20s(monkeypatch, (10, 10))
    ui._apply_custom_effect(CustomEffect(**BOLT))
    assert tiger["hp"] == tiger["max_hp"]
    assert tiger["ac_above"] == 13, "what the miss showed, without the bonus"


# ---------------------------------------------------------------------------
# The dialog's reminders, for rolls made at the table


def _chips(dlg, row: str) -> dict[str, QPushButton]:
    widget = dlg.findChild(QWidget, row)
    return {b.text().replace("&", ""): b for b in widget.findChildren(QPushButton)}


def _infos(dlg) -> list[str]:
    rows = dlg.findChildren(QLabel, "targetRowInfo")
    return [label.text() for label in rows if label.isVisibleTo(dlg)]


def test_the_dialog_shows_what_conditions_do_to_each_roll(fight, monkeypatch):
    ui, pirate, tiger = fight
    tiger["conditions"].append("Restrained")
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _chips(dlg, "saveAbilityButtons")["DEX"].click()
    assert _infos(dlg) == ["DEX +3, Disadvantage"]
    _chips(dlg, "saveAbilityButtons")["WIS"].click()
    assert "," not in _infos(dlg)[0]  # only Dexterity saves
    _chips(dlg, "rollKindButtons")[ATTACK_ROLL].click()
    assert _infos(dlg) == ["AC 15, Advantage"]


def test_the_dialog_says_a_save_fails_without_a_roll(fight, monkeypatch):
    ui, _, tiger = fight
    tiger["conditions"].append("Stunned")
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _chips(dlg, "saveAbilityButtons")["DEX"].click()
    assert _infos(dlg) == ["DEX fails"]


# ---------------------------------------------------------------------------
# A monster's action buttons (TurnPanelMixin._roll_action)

BITE = MonsterAction("Bite", "A bite.", to_hit=5)


def test_a_monsters_attack_on_a_restrained_target_has_advantage(fight, monkeypatch):
    ui, pirate, tiger = fight
    tiger["conditions"].append("Restrained")
    _d20s(monkeypatch, (4, 12))
    ui._roll_action(BITE, pirate)
    text = ui._action_result_label.text()
    assert "rolled 17 (12+5)" in text
    assert "HIT" in text
    assert "Tiger is Restrained: Advantage" in text


def test_a_monsters_attack_counts_the_targets_cover(fight, monkeypatch):
    """Half Cover: "+2 bonus to AC". A 15 meets AC 15 but not 17."""
    ui, pirate, tiger = fight
    tiger["visibility_states"] = [Visibility.HALF_COVER.value]
    _d20s(monkeypatch, (10, 10))
    ui._roll_action(BITE, pirate)
    text = ui._action_result_label.text()
    assert "vs AC 17" in text
    assert "MISS" in text


def test_a_poisoned_monsters_action_has_disadvantage_with_several_targets(
    tmp_path, monkeypatch
):
    ui = make_ui(tmp_path, [Pirate(), Tiger(), Tiger()])
    pirate, *tigers = ui.characters
    ui._set_targets(tigers)
    pirate["conditions"].append("Poisoned")
    _d20s(monkeypatch, (12, 4))
    ui._roll_action(BITE, pirate)
    assert "rolled 9 (4+5)" in ui._action_result_label.text()


def test_a_longer_name_for_stunned_still_breaks_concentration(fight):
    """Incapacitated: "Your Concentration is broken.\" """
    ui, pirate, _ = fight
    pirate["conditions"].append("Concentrating")
    ui._add_condition_to(pirate, "Stunned by Stunning Strike")
    assert "Concentrating" not in pirate["conditions"]
