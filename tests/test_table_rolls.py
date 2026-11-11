"""Every roll can be made at the table (Notes/combat-effects-plan.md, design
principle 13 and Phase 8): whatever the simulator rolls, the GM can give it
a number rolled at the table instead.

- 8.1: a hit's extra damage (Hunter's Mark's 1d6 Force, Divine Favor's 1d4
  Radiant) has a box of its own in the Custom Effect dialog. A number typed
  there is added as it is, Critical Hit or not, even to a damage total typed
  in; blank rolls it, unless the damage is a total typed in (Decision 4).
- 8.2: a triggered row's own roll (Deflect Attacks' 1d10 + 8) has a box in
  the pop-up; blank rolls it.
- 8.3: with the setting monsters_roll_turn_dice off, a monster's recharge
  and its repeat saves are turn reminders, rolled at the table, as a
  player's repeat saves are."""

import random
from dataclasses import replace

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTreeWidget,
    QWidget,
)

from Builds.Characters.Y2024_Paladin_Devotion_Edmund import (
    Y2024PaladinDevotionEdmundCharacterBuilder as Edmund,
)
from CharacterContent.Spells.SpellFactory import SpellFactory
from Combat.Combatants import Pirate, Tiger
from Combat.CombatUIQt import turn_panel_mixin as turn_panel
from Combat.CombatUIQt.monster_actions import DamageRoll
from Combat.CombatUIQt.saves import CustomEffect, roll_extra_damage
from Combat.CombatUIQt.trigger_prompt import TriggerPrompt
from Combat.Effects.active_effects import give_modifiers, note_origin, repeat_saves
from Combat.Effects.modifiers import hit_plan, hit_point_maximum
from Combat.Effects.triggers import TriggerChoice
from Core.Definitions import DamageType
from Model.Content.CombatModifiers import ExtraDamageFrom, HitPointMaximum
from tests._combat_ui import make_ui, open_dialog
from tests.test_hit_by_triggers import _lines as _hit_by_lines
from tests.test_hit_by_triggers import _typed_hit
from tests.test_hit_by_triggers import party  # noqa: F401  (a fixture)

MARK = "Pirate's Hunter's Mark"


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)
    monkeypatch.setattr(QMessageBox, "question", refuse)


@pytest.fixture
def fight(tmp_path):
    """A Pirate (15, the source) who has cast Hunter's Mark on a Tiger (10,
    AC 15, the target)."""
    ui = make_ui(tmp_path, [Pirate(), Tiger()])
    pirate, tiger = ui.characters
    for char, value in zip(ui.characters, (15, 10)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    ui._select_character(pirate)
    ui._set_targets([tiger])
    ui._apply_cast_spell(SpellFactory.create("Hunter's Mark"))
    ui._set_targets([tiger])
    tiger["ac"] = 15
    return ui, pirate, tiger


def _lines(ui) -> list[str]:
    return [e["text"].split("] ", 1)[-1] for e in ui._read_log()["round_1"]]


def _attack(tiger, extra: int | None = None, **kwargs) -> CustomEffect:
    """+5 to hit, 5 Slashing (9 on a Critical Hit), with the mark's extra
    damage typed in when `extra` is given."""
    typed = {} if extra is None else {id(tiger): {MARK: extra}}
    fields = {
        "name": "Scimitar",
        "damage": [(5, "Slashing")],
        "critical_damage": [(9, "Slashing")],
        "attack_bonus": 5,
        "typed_extras": typed,
    }
    return CustomEffect(**{**fields, **kwargs})


def _d20s_only(monkeypatch, d20: int):
    """Every d20 is `d20`; any other die fails the test, as nothing else
    should be rolled."""

    def roll(low, high):
        assert high == 20, f"a d{high} was rolled"
        return d20

    monkeypatch.setattr(random, "randint", roll)


# ---------------------------------------------------------------------------
# 8.1 A hit's extra damage


def test_extra_damage_rolled_at_the_table_is_added_as_typed():
    attacker = {"name": "Pirate", "conditions": []}
    target = {"name": "Tiger", "conditions": ["Hunter's Mark"]}
    give_modifiers(target, "Hunter's Mark", (ExtraDamageFrom("1d6", DamageType.FORCE),))
    note_origin(target, "Hunter's Mark", caster="Pirate")
    plan = hit_plan(attacker, target, None, {MARK: 4})
    assert plan.at_table == (MARK,)
    parts, lines = roll_extra_damage(plan, critical=True)
    assert parts == [(4, "Force")], "a total typed in isn't doubled"
    assert lines == (f"{MARK}: +4 Force (rolled at the table)",)


def test_a_typed_extra_is_added_and_nothing_else_is_rolled(fight, monkeypatch):
    ui, _, tiger = fight
    _d20s_only(monkeypatch, 15)
    ui._apply_custom_effect(_attack(tiger, 3))
    assert tiger["hp"] == 30 - 5 - 3
    assert f"{MARK}: +3 Force (rolled at the table)" in _lines(ui)


def test_a_typed_extra_is_added_to_a_typed_damage_total(fight, monkeypatch):
    """The weapon's 7 and the mark's 4, both rolled at the table."""
    ui, _, tiger = fight
    _d20s_only(monkeypatch, 15)
    ui._apply_custom_effect(
        _attack(tiger, 4, damage=[(7, "Slashing")], typed_damage=True)
    )
    assert tiger["hp"] == 30 - 7 - 4


def test_a_typed_damage_total_says_the_extra_it_has(fight, monkeypatch):
    """Blank, under a total typed in: not rolled (Decision 4), and said."""
    ui, _, tiger = fight
    _d20s_only(monkeypatch, 15)
    ui._apply_custom_effect(_attack(tiger, damage=[(7, "Slashing")], typed_damage=True))
    assert tiger["hp"] == 30 - 7
    assert f"{MARK}: not rolled, as the damage total typed has it" in _lines(ui)


def test_a_typed_zero_leaves_the_extra_out(fight, monkeypatch):
    ui, _, tiger = fight
    _d20s_only(monkeypatch, 15)
    ui._apply_custom_effect(_attack(tiger, 0))
    assert tiger["hp"] == 30 - 5


def test_a_typed_extra_goes_with_the_first_of_several_times(fight, monkeypatch):
    """Times 2: as every total typed in, it's the first attack's; the second
    rolls its own."""
    ui, _, tiger = fight
    monkeypatch.setattr(random, "randint", lambda low, high: 15 if high == 20 else 2)
    first = _attack(tiger, 6, name="Scimitar (1 of 2)")
    second = _attack(tiger, name="Scimitar (2 of 2)")
    ui._apply_custom_effects([first, second])
    assert tiger["hp"] == 30 - (5 + 6) - (5 + 2)


@pytest.fixture
def paladin(tmp_path, monkeypatch):
    """Edmund (15) with Divine Favor cast, the source, targeting a Tiger
    (10, AC 15); every d20 a 15 and every other die a 2."""
    ui = make_ui(tmp_path, [Tiger()], [Edmund().build()])
    edmund, tiger = ui.characters
    ui._initiative_inputs[id(edmund)].setText("15")
    ui._initiative_inputs[id(tiger)].setText("10")
    ui._start_combat()
    ui._select_character(edmund)
    ui._set_targets([])
    ui._apply_cast_spell(SpellFactory.create("Divine Favor"))
    ui._set_targets([tiger])
    tiger["ac"] = 15
    monkeypatch.undo()  # the dialog's exec, for open_dialog
    monkeypatch.setattr(random, "randint", lambda low, high: 15 if high == 20 else 2)
    return ui, edmund, tiger


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


def _extra_box(dlg) -> QLineEdit:
    (box,) = dlg.findChildren(QLineEdit, "typedExtra")
    return box


def test_the_dialog_has_a_box_for_the_extra_on_the_targets_row(paladin, monkeypatch):
    ui, _, _ = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Longsword")
    box = _extra_box(dlg)
    assert box.isVisibleTo(dlg)
    assert box.placeholderText() == "Rolled, or blank to roll"
    (info,) = dlg.findChildren(QLabel, "extraRowInfo")
    assert info.text() == "Divine Favor: +1d4 Radiant on a weapon hit"
    assert box.toolTip().startswith("Edmund's Divine Favor: what was rolled")
    chips = dlg.findChild(QWidget, "rollKindButtons")
    buttons = {b.text().replace("&", ""): b for b in chips.findChildren(QPushButton)}
    buttons["Saving throw"].click()
    assert not box.isVisibleTo(dlg), "only an attack roll's hit has it"


def test_the_dialogs_typed_extra_is_dealt(paladin, monkeypatch):
    """The Longsword's 1d8 + 4 (a 2: 6) rolled here, Divine Favor's 3 at the
    table."""
    ui, _, tiger = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Longsword")
    _extra_box(dlg).setText("3")
    _apply(dlg)
    assert tiger["hp"] == 30 - 6 - 3
    assert any(
        "Divine Favor: +3 Radiant (rolled at the table)" in e for e in _lines(ui)
    )


def test_the_dialog_refuses_an_extra_that_isnt_an_amount(paladin, monkeypatch):
    ui, _, tiger = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Longsword")
    _extra_box(dlg).setText("lots")
    _apply(dlg)
    assert tiger["hp"] == 30
    problems = [lbl.text() for lbl in dlg.findChildren(QLabel, "statusLabel")]
    assert any("'lots' isn't an amount of damage" in text for text in problems)


def test_the_dialog_has_no_extra_box_without_extra_damage(tmp_path, monkeypatch):
    ui = make_ui(tmp_path, [Pirate(), Tiger()])
    pirate, tiger = ui.characters
    ui._select_character(pirate)
    ui._set_targets([tiger])
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    assert dlg.findChildren(QLineEdit, "typedExtra") == []


# ---------------------------------------------------------------------------
# 8.2 A triggered row's own roll


class Rolled:
    """Stands in for the pop-up: applies every firing, with `rolled` typed
    in for each."""

    def __init__(self, rolled: int | None):
        self.rolled = rolled

    def __call__(self, firings):
        rolled = () if self.rolled is None else tuple((f, self.rolled) for f in firings)
        return TriggerChoice(apply=tuple(firings), rolled=rolled)


def test_deflect_attacks_rolled_at_the_table_takes_that_off(party, monkeypatch):
    ui, _, kivi, _ = party
    monkeypatch.setattr(ui, "_ask_triggers", Rolled(11))

    def no_roll(dice, critical=False):
        raise AssertionError("nothing should be rolled here")

    monkeypatch.setattr(turn_panel, "roll_dice", no_roll)
    hp = kivi["hp"]
    _typed_hit(ui, kivi)
    assert kivi["hp"] == hp - 2  # 13 - 11
    assert any(
        "Deflect Attacks takes 11 off the damage (1d10 + 8, rolled at the table)"
        in line
        for line in _hit_by_lines(ui)
    )


def test_the_pop_up_has_a_box_for_a_rows_own_roll(party, monkeypatch):
    ui, _, kivi, _ = party
    asked = []

    def record(firings):
        asked.extend(firings)
        return TriggerChoice()

    monkeypatch.setattr(ui, "_ask_triggers", record)
    _typed_hit(ui, kivi)
    prompt = TriggerPrompt(None, asked)
    (box,) = prompt.findChildren(QLineEdit, "triggerRolled")
    assert box.placeholderText() == "1d10 + 8, blank rolls"
    box.setText("7 + 8")
    prompt.apply_button.click()
    choice = prompt.choice()
    assert choice.rolled_for(asked[0]) == 15
    box.setText("")
    assert prompt.choice().rolled_for(asked[0]) is None


# ---------------------------------------------------------------------------
# 8.3 Dice nobody is asked about


BREATH = {
    "name": "Fire Breath (Recharge 5\N{EN DASH}6)",
    "description": "Dexterity Saving Throw: DC 14, each creature in a 30-foot Cone."
    " Failure: 27 (6d8) Fire damage. Success: Half damage.",
}


def test_with_the_setting_off_a_recharge_is_a_reminder(fight, monkeypatch):
    ui, pirate, _ = fight
    ui.settings.monsters_roll_turn_dice = False
    pirate.update(actions=[BREATH])
    pirate["spent_abilities"] = {BREATH["name"]: 1}
    _d20s_only(monkeypatch, 10)  # no d6
    ui._advance_turn()
    ui._advance_turn()  # the Pirate's turn again
    ui._refresh_views()
    assert pirate["spent_abilities"] == {BREATH["name"]: 1}
    assert (
        f"{BREATH['name']}: roll its recharge (a d6 of 5 or more), ↺ if it comes back"
        in ui._turn_reminders_label.text()
    )


def test_with_the_setting_off_a_monsters_repeat_save_is_a_reminder(fight, monkeypatch):
    ui, _, tiger = fight
    ui.settings.monsters_roll_turn_dice = False
    monkeypatch.setattr(random, "randint", lambda low, high: 1)
    ui._apply_custom_effect(
        CustomEffect(
            name="Hold", condition="Paralyzed", ability="WIS", dc=15, repeat_save=True
        )
    )
    _d20s_only(monkeypatch, 20)
    ui._advance_turn()  # the Tiger's turn starts
    ui._advance_turn()  # ...and ends: no roll, a reminder
    ui._refresh_views()
    assert "Paralyzed" in tiger["conditions"]
    assert repeat_saves(tiger)
    assert (
        "Tiger: DC 15 Wisdom save to end Paralyzed" in ui._turn_reminders_label.text()
    )


def test_the_dialog_fits_with_an_extra_box_for_each_of_eight_targets(
    tmp_path, monkeypatch
):
    """Divine Favor is on its caster, so every target has a box: they scroll,
    as the attack rows do, and the dialog still fits a 600-high window."""
    pirates = []
    for i in range(8):
        pirate = Pirate()
        pirate.set_name(f"Pirate {i}")
        pirates.append(pirate)
    ui = make_ui(tmp_path, pirates, [Edmund().build()])
    for i, char in enumerate(ui.characters):
        ui._initiative_inputs[id(char)].setText(str(20 - i))
    ui._start_combat()
    edmund = next(c for c in ui.characters if c.get("_is_player"))
    ui._select_character(edmund)
    ui._set_targets([])
    ui._apply_cast_spell(SpellFactory.create("Divine Favor"))
    ui._set_targets([c for c in ui.characters if c is not edmund])
    monkeypatch.undo()
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Longsword")
    assert len(dlg.findChildren(QLineEdit, "typedExtra")) == 8
    assert dlg.layout().totalHeightForWidth(dlg.width()) <= 600


def test_the_dialog_fits_with_two_extras_on_one_target(paladin, monkeypatch):
    """Edmund's Divine Favor and his Hunter's Mark on the Tiger: a row each."""
    ui, edmund, tiger = paladin
    tiger["conditions"].append("Hunter's Mark")
    give_modifiers(tiger, "Hunter's Mark", (ExtraDamageFrom("1d6", DamageType.FORCE),))
    note_origin(tiger, "Hunter's Mark", caster=edmund["name"])
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Longsword")
    infos = [lbl.text() for lbl in dlg.findChildren(QLabel, "extraRowInfo")]
    assert sorted(infos) == [
        "Divine Favor: +1d4 Radiant on a weapon hit",
        "Hunter's Mark: +1d6 Force on a hit",
    ]
    assert dlg.layout().totalHeightForWidth(dlg.width()) <= 600


# ---------------------------------------------------------------------------
# 8.4 Anyone's initiative, set to what was rolled at the table


def test_set_initiative_moves_a_turn_and_keeps_whose_turn_it_is(fight):
    """The Pirate (15) has the turn; the Tiger's 10 becomes 20: it goes
    first from now on, and it's still the Pirate's turn."""
    ui, pirate, tiger = fight
    ui._set_initiative(tiger, 20)
    assert ui.initiative_order == [tiger, pirate]
    assert ui.initiative_order[ui.current_turn_idx] is pirate
    assert "Tiger's initiative is 20" in _lines(ui)
    ui._undo_last()
    assert ui.initiative_order == [pirate, tiger]
    assert ui.initiative_order[ui.current_turn_idx] is pirate


def test_set_initiative_on_the_current_turn_keeps_it(fight):
    ui, pirate, tiger = fight
    ui._set_initiative(pirate, 1)
    assert ui.initiative_order == [tiger, pirate]
    assert ui.initiative_order[ui.current_turn_idx] is pirate


def test_the_card_menu_asks_for_the_initiative(fight, monkeypatch):
    ui, _, tiger = fight
    monkeypatch.setattr(QInputDialog, "getInt", lambda *args: (18, True))
    menu = ui._card_menu(tiger)
    action = next(a for a in menu.actions() if a.text() == "Set initiative...")
    action.trigger()
    assert tiger["_initiative"] == 18
    assert ui.initiative_order[0] is tiger


def test_no_initiative_to_set_before_the_fight(tmp_path):
    ui = make_ui(tmp_path, [Pirate(), Tiger()])
    pirate, _ = ui.characters
    assert not ui._can_set_initiative(pirate)
    assert not any(
        a.text() == "Set initiative..." for a in ui._card_menu(pirate).actions()
    )


# ---------------------------------------------------------------------------
# 8.5 A roll for each of the Times


def _box(dlg, name: str) -> QLineEdit:
    (box,) = dlg.findChildren(QLineEdit, name)
    return box


def test_each_time_takes_its_own_typed_attack_and_extra(paladin, monkeypatch):
    """Times 2, "nat 1, nat 20": the first misses, the second is a Critical
    Hit (2d8 + 4 = 8, every die a 2) with Divine Favor's 5 typed for it."""
    ui, _, tiger = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Longsword")
    dlg.findChild(QSpinBox, "effectTimes").setValue(2)
    _box(dlg, "typedAttack").setText("nat 1, nat 20")
    _extra_box(dlg).setText(", 5")
    _apply(dlg)
    assert tiger["hp"] == 30 - 8 - 5
    lines = _lines(ui)
    assert any("Divine Favor: +5 Radiant (rolled at the table)" in e for e in lines)


def test_a_short_list_rolls_the_rest(paladin, monkeypatch):
    """Times 2, "nat 1": the second attack is rolled (a 15 hits AC 15)."""
    ui, _, tiger = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Longsword")
    dlg.findChild(QSpinBox, "effectTimes").setValue(2)
    _box(dlg, "typedAttack").setText("nat 1")
    _apply(dlg)
    assert tiger["hp"] == 30 - 6 - 2


def test_more_rolls_than_times_are_refused(paladin, monkeypatch):
    ui, _, tiger = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Longsword")
    _box(dlg, "typedAttack").setText("17, 9")
    _apply(dlg)
    assert tiger["hp"] == 30
    problems = [lbl.text() for lbl in dlg.findChildren(QLabel, "statusLabel")]
    assert any("'17, 9': 2 rolls for Times 1." in text for text in problems)


# ---------------------------------------------------------------------------
# 8.6 Dice Hit Points


def test_a_hit_point_maximum_rolled_at_the_table_is_given_as_typed(fight, monkeypatch):
    """Heroes' Feast's 2d10, rolled at the table as 12: nothing rolled here."""
    ui, pirate, tiger = fight
    _d20s_only(monkeypatch, 10)
    tiger["conditions"].append("Heroes' Feast")
    ui._give_badge_modifiers(
        tiger, "Heroes' Feast", (HitPointMaximum("2d10"),), rolled_maximum=12
    )
    assert hit_point_maximum(tiger) == 30 + 12


def test_the_maximum_box_shows_only_for_a_pick_that_rolls_one(paladin, monkeypatch):
    ui, _, _ = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Longsword")
    assert not _box(dlg, "typedHitPointMaximum").isVisibleTo(dlg)


def _heroism_with_dice(monkeypatch, dice: str):
    """Heroism's Temporary Hit Points as `dice` instead of a number."""
    real = turn_panel.trigger_option

    def with_dice(caster, source, effect):
        option = real(caster, source, effect)
        return replace(option, rolls=(DamageRoll(dice, None),))

    monkeypatch.setattr(turn_panel, "trigger_option", with_dice)


def test_a_players_dice_hit_points_are_a_button_not_rolled(tmp_path, monkeypatch):
    ui = make_ui(tmp_path, [Tiger()], [Edmund().build()])
    edmund, tiger = ui.characters
    ui._initiative_inputs[id(edmund)].setText("15")
    ui._initiative_inputs[id(tiger)].setText("10")
    ui._start_combat()
    ui._select_character(edmund)
    ui._set_targets([edmund])
    ui._apply_cast_spell(SpellFactory.create("Heroism"), 1)
    _heroism_with_dice(monkeypatch, "1d4")
    _d20s_only(monkeypatch, 10)  # no d4
    ui._advance_turn()
    ui._advance_turn()  # Edmund's turn: a button, no temp HP given
    assert edmund.get("temp_hp", 0) == 0
    assert any("Heroism" in f.prompt for f in ui._turn_prompts)
