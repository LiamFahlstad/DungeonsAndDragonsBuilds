"""The Custom dialog as a save-or-suffer effect (saves.py,
ConditionsMixin._apply_custom_effect): a saving throw rolled for every target, or
an attack roll against each one's AC, damage rolled once for all of them, and a
condition on those who failed or were hit, all one undo. Expected values come
from the rules: Saving-Throw, Critical-Hit and the Paralyzed, Petrified, Stunned,
Unconscious and Restrained glossary entries."""

import random

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QShortcut
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTextBrowser,
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
)

from Builds.Characters.Y2024_Paladin_Devotion_Edmund import (
    Y2024PaladinDevotionEdmundCharacterBuilder as Edmund,
)
from CharacterContent.Spells.SpellFactory import SpellFactory
from Combat.Combatants import Pirate, Tiger
from Combat.CombatUIQt.amounts import AmountError
from Combat.Definitions import Action
from Combat.Effects.active_effects import CUSTOM, SPELL, active_effects
from Combat.Effects.active_effects import repeat_saves, timed_effects, timers
from Combat.CombatUIQt.attack_rolls import AttackRoll
from Combat.CombatUIQt.saves import (
    ATTACK_ROLL,
    DAMAGE_AMOUNT,
    FEATURE,
    HEALING,
    MONSTER_ACTION,
    SAVING_THROW,
    TEMP_HP,
    CustomEffect,
    EffectOption,
    is_immune_to,
    known_attack_bonus,
    known_save_dc,
    read_damage,
    roll_attack,
    roll_save,
    rolled_damage,
    save_modifier,
)
from Core.Definitions import Condition, DamageType
from Model.Content.Feature import Feature
from Model.Creatures.Combatants import DamageTypeEntry, Visibility
from tests._combat_ui import answer_out_of_resources, make_ui, open_dialog

FIRE = DamageType.FIRE.value


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    """A modal dialog would block the test forever; fail it instead."""

    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)


def _named(combatant, name: str):
    combatant.set_name(name)
    return combatant


@pytest.fixture
def fight(tmp_path):
    """A Pirate (15, the source) targeting a Tiger (10) and a Bandit (5). The
    Tiger adds +3 to Dexterity saves, the Bandit +3 too."""
    ui = make_ui(tmp_path, [Pirate(), Tiger(), _named(Pirate(), "Bandit")])
    pirate, tiger, bandit = ui.characters
    for char, value in zip(ui.characters, (15, 10, 5)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    ui._select_target_character(tiger)
    ui._select_target_character(bandit, ctrl=True)
    tiger["Saving Throws"] = {"DEX": 3}
    bandit["Saving Throws"] = {"DEX": 3}
    return ui, pirate, tiger, bandit


def _d20s(monkeypatch, *rolls: int):
    """random.randint gives these, each repeated for the two dice a save throws
    whether or not it needs both."""
    results = iter(value for roll in rolls for value in (roll, roll))
    monkeypatch.setattr(random, "randint", lambda low, high: next(results))


def _log(ui) -> str:
    return str(ui._read_log())


def _custom_notes(char: dict) -> dict[str, str | None]:
    """The notes typed for char's badges, by badge."""
    return {
        e["name"]: e["tooltip"]
        for e in active_effects(char)
        if e["tooltip_from"] == CUSTOM
    }


FIREBALL = {"damage": [(20, FIRE)], "ability": "DEX", "dc": 15}


# ---------------------------------------------------------------------------
# Saving throw modifiers and rolls


@pytest.mark.parametrize(
    "char, ability, modifier",
    [
        ({"Saving Throws": {"DEX": 6}, "Ability Scores": {"DEX": 10}}, "DEX", 6),
        ({"Saving Throws": {"WIS": 6}, "Ability Scores": {"DEX": 16}}, "DEX", 3),
        ({"Saving Throws": {}, "Ability Scores": {"STR": 8, "DEX": 16}}, "STR", -1),
        ({"Saving Throws": {}, "Ability Scores": {"STR": 10, "DEX": 10}}, "STR", 0),
        ({}, "STR", 0),
    ],
)
def test_save_modifier(char, ability, modifier):
    assert save_modifier(char, ability) == modifier


@pytest.mark.parametrize("d20, success", [(12, True), (11, False)])
def test_meeting_the_dc_saves(monkeypatch, d20, success):
    _d20s(monkeypatch, d20)
    result = roll_save({"Saving Throws": {"DEX": 3}}, "DEX", 15, "Neutral")
    assert result.success is success
    assert result.total == d20 + 3


def test_a_natural_20_is_nothing_special_on_a_save(monkeypatch):
    _d20s(monkeypatch, 20)
    assert not roll_save({"Saving Throws": {"DEX": -1}}, "DEX", 25, "Neutral").success


def test_a_natural_1_is_nothing_special_on_a_save(monkeypatch):
    _d20s(monkeypatch, 1)
    assert roll_save({"Saving Throws": {"DEX": 9}}, "DEX", 10, "Neutral").success


@pytest.mark.parametrize(
    "mode, total", [("Neutral", 4), ("Advantage", 17), ("Disadvantage", 4)]
)
def test_roll_modes(monkeypatch, mode, total):
    rolls = iter([4, 17])
    monkeypatch.setattr(random, "randint", lambda low, high: next(rolls))
    assert roll_save({}, "DEX", 10, mode).total == total


@pytest.mark.parametrize(
    "condition", ["Paralyzed", "Petrified", "Stunned", "Unconscious"]
)
@pytest.mark.parametrize("ability", ["STR", "DEX"])
def test_automatic_failures(condition, ability):
    result = roll_save(
        {"conditions": [condition], "Saving Throws": {ability: 99}},
        ability,
        5,
        "Neutral",
    )
    assert not result.success
    assert result.total is None
    assert condition in result.note


def test_an_automatic_failure_beats_a_typed_total():
    assert not roll_save({"conditions": ["Stunned"]}, "DEX", 5, "Neutral", 30).success


def test_automatic_failure_is_only_strength_and_dexterity(monkeypatch):
    _d20s(monkeypatch, 15)
    assert roll_save({"conditions": ["Stunned"]}, "WIS", 10, "Neutral").success


def test_restrained_gives_disadvantage_on_dexterity(monkeypatch):
    rolls = iter([4, 17])
    monkeypatch.setattr(random, "randint", lambda low, high: next(rolls))
    result = roll_save({"conditions": ["Restrained"]}, "DEX", 10, "Neutral")
    assert result.total == 4
    assert "Disadvantage" in result.note


def test_restrained_cancels_advantage(monkeypatch):
    rolls = iter([4, 17])
    monkeypatch.setattr(random, "randint", lambda low, high: next(rolls))
    assert roll_save({"conditions": ["Restrained"]}, "DEX", 10, "Advantage").total == 4


def test_restrained_is_only_dexterity(monkeypatch):
    rolls = iter([17, 4])
    monkeypatch.setattr(random, "randint", lambda low, high: next(rolls))
    assert roll_save({"conditions": ["Restrained"]}, "WIS", 10, "Neutral").total == 17


def test_a_typed_total_is_used_as_it_is():
    assert (
        roll_save({"Saving Throws": {"DEX": 99}}, "DEX", 15, "Neutral", 14).total == 14
    )
    assert roll_save({}, "DEX", 15, "Neutral", 15).success


@pytest.mark.parametrize(
    "immunities, immune",
    [
        ([Condition.PRONE], True),
        (["Prone"], True),
        ([Condition.CHARMED], False),
        (None, False),
    ],
)
def test_is_immune_to(immunities, immune):
    assert is_immune_to({"condition_immunities": immunities}, "Prone") is immune


# ---------------------------------------------------------------------------
# Damage text


def test_dice_are_rolled(monkeypatch):
    monkeypatch.setattr(random, "randint", lambda low, high: 3)
    assert rolled_damage("8d6 fire") == [(24, FIRE)]
    assert rolled_damage("2d6 + 3 fi") == [(9, FIRE)]
    assert rolled_damage("2d6 sl + 1d4 fi") == [
        (6, DamageType.SLASHING.value),
        (3, FIRE),
    ]


def test_the_dropdown_gives_a_type_to_what_has_none(monkeypatch):
    monkeypatch.setattr(random, "randint", lambda low, high: 3)
    assert read_damage("8d6", FIRE) == ([(24, FIRE)], "")
    assert read_damage("2d6 fire", FIRE)[0] == [(6, FIRE)]


def test_a_dropdown_that_disagrees_with_the_text_is_refused():
    assert read_damage("10 fire", DamageType.COLD.value) == (
        [],
        "The damage says Fire, the dropdown Cold.",
    )


@pytest.mark.parametrize(
    "text, parts",
    [
        ("2d6 + 1d4 fi", [(9, FIRE)]),
        ("1d6+2 fi", [(5, FIRE)]),
        ("20 - 2d6 + 3 fi", [(17, FIRE)]),
        ("1d8+1d8+1d8 fi", [(9, FIRE)]),
        ("2d6 + 3 fi + 1d4 co", [(9, FIRE), (3, DamageType.COLD.value)]),
    ],
)
def test_sums_of_dice(monkeypatch, text, parts):
    monkeypatch.setattr(random, "randint", lambda low, high: 3)
    assert rolled_damage(text) == parts


def test_a_low_roll_is_no_damage_not_a_mistake(monkeypatch):
    monkeypatch.setattr(random, "randint", lambda low, high: 1)
    assert rolled_damage("1d4 - 2 fi") == [(0, FIRE)]


def test_a_die_of_no_sides_is_refused():
    with pytest.raises(AmountError):
        rolled_damage("1d0 fi")


def test_a_plain_amount_stays_as_it_is():
    assert rolled_damage("28 fi") == [(28, FIRE)]


def test_damage_needs_a_type():
    assert read_damage("8d6")[1] == "Damage needs a type: pick one, or type 8d6 fire."
    assert read_damage("")[0] == [] and read_damage("")[1] == ""
    assert "isn't a damage type" in read_damage("8d6 zz")[1]


def test_bad_damage_raises():
    with pytest.raises(AmountError):
        rolled_damage("fire")


# ---------------------------------------------------------------------------
# Applying it


def test_each_target_rolls_and_takes_its_own_result(fight, monkeypatch):
    ui, _, tiger, bandit = fight
    _d20s(monkeypatch, 12, 11)  # the Tiger's 15 saves, the Bandit's 14 fails
    ui._apply_custom_effect(CustomEffect(**FIREBALL))
    assert tiger["hp"] == tiger["max_hp"] - 10
    assert bandit["hp"] == bandit["max_hp"] - 20
    assert "Tiger makes a DC 15 Dexterity save, rolled 15" in _log(ui)
    assert "fails a DC 15 Dexterity save, rolled 14" in _log(ui)


def test_a_save_can_avoid_the_damage(fight, monkeypatch):
    ui, _, tiger, _ = fight
    _d20s(monkeypatch, 20, 20)
    ui._apply_custom_effect(CustomEffect(**FIREBALL, half_on_save=False))
    assert tiger["hp"] == tiger["max_hp"]


def test_resistance_counts_after_the_save(fight, monkeypatch):
    ui, _, tiger, _ = fight
    tiger["damage_resistances"] = [DamageTypeEntry(damage_types=[DamageType.FIRE])]
    _d20s(monkeypatch, 20, 20)
    ui._apply_custom_effect(CustomEffect(damage=[(25, FIRE)], ability="DEX", dc=15))
    assert tiger["hp"] == tiger["max_hp"] - 6  # 25 -> 12 -> 6


def test_a_condition_lands_only_on_a_failed_save(fight, monkeypatch):
    ui, _, tiger, bandit = fight
    _d20s(monkeypatch, 20, 1)
    ui._apply_custom_effect(
        CustomEffect(condition="Prone", ability="DEX", dc=15, notes="Knocked flat")
    )
    assert "Prone" not in tiger["conditions"]
    assert "Prone" in bandit["conditions"]
    assert _custom_notes(bandit) == {"Prone": "Knocked flat"}


def test_a_condition_has_its_duration(fight, monkeypatch):
    ui, _, _, bandit = fight
    _d20s(monkeypatch, 1, 1)
    ui._apply_custom_effect(
        CustomEffect(condition="Hexed", ability="DEX", dc=15, duration={"seconds": 60})
    )
    assert timers(bandit)[0]["time_left"] == 60


def test_without_a_save_everyone_takes_it_all(fight):
    ui, _, tiger, bandit = fight
    ui._apply_custom_effect(CustomEffect(condition="Prone", damage=[(8, FIRE)]))
    for target in (tiger, bandit):
        assert target["hp"] == target["max_hp"] - 8
        assert "Prone" in target["conditions"]


def test_a_creature_immune_to_the_condition_is_spared(fight, monkeypatch):
    ui, _, tiger, _ = fight
    tiger["condition_immunities"] = [Condition.PRONE]
    _d20s(monkeypatch, 1, 1)
    ui._apply_custom_effect(CustomEffect(condition="Prone", ability="DEX", dc=15))
    assert "Prone" not in tiger["conditions"]
    assert "Tiger is immune to Prone" in _log(ui)


def test_the_dead_get_no_condition(fight, monkeypatch):
    ui, _, tiger, _ = fight
    tiger["hp"] = 1
    _d20s(monkeypatch, 1, 1)
    ui._apply_custom_effect(
        CustomEffect(damage=[(20, FIRE)], condition="Prone", ability="DEX", dc=15)
    )
    assert "Prone" not in tiger["conditions"]


def test_a_dead_target_rolls_nothing(fight, monkeypatch):
    ui, _, tiger, bandit = fight
    tiger["hp"] = 0
    _d20s(monkeypatch, 1)  # only the Bandit rolls
    ui._apply_custom_effect(CustomEffect(**FIREBALL, condition="Prone"))
    assert "Prone" not in tiger["conditions"]
    assert "Tiger fails" not in _log(ui) and "Tiger makes" not in _log(ui)
    assert bandit["hp"] == bandit["max_hp"] - 20


def test_a_character_with_no_spellcasting_has_no_dc():
    class NoCaster:
        spell_casting_ability = None

    assert known_save_dc({"_stat_block": NoCaster()}) is None


def test_damage_forces_a_concentration_save(fight, monkeypatch):
    ui, _, tiger, _ = fight
    tiger["conditions"].append("Concentrating")
    _d20s(monkeypatch, 1, 1)
    ui._apply_custom_effect(CustomEffect(**FIREBALL))
    assert tiger["concentration_checks"] == [10]


def test_it_is_one_undo(fight, monkeypatch):
    ui, _, tiger, bandit = fight
    _d20s(monkeypatch, 20, 1)
    ui._apply_custom_effect(CustomEffect(**FIREBALL, condition="Prone"))
    ui._undo_last()
    assert tiger["hp"] == tiger["max_hp"]
    assert bandit["hp"] == bandit["max_hp"]
    assert "Prone" not in bandit["conditions"]
    assert ui.history == []
    assert "Dexterity" not in _log(ui)


def test_a_typed_total_is_used(fight, monkeypatch):
    ui, _, tiger, bandit = fight
    _d20s(monkeypatch, 1)  # the Tiger's: the Bandit's total is typed
    ui._apply_custom_effect(CustomEffect(**FIREBALL, typed_totals={id(bandit): 18}))
    assert tiger["hp"] == tiger["max_hp"] - 20
    assert bandit["hp"] == bandit["max_hp"] - 10


def test_legendary_resistance_turns_a_failure_into_a_save(fight, monkeypatch):
    ui, _, tiger, _ = fight
    tiger["legendary_resistances"] = 2
    _d20s(monkeypatch, 1, 1)
    ui._apply_custom_effect(CustomEffect(**FIREBALL, use_legendary_resistance=True))
    assert tiger["hp"] == tiger["max_hp"] - 10
    assert tiger["legendary_resistances_left"] == 1


def test_legendary_resistance_isnt_spent_on_a_success(fight, monkeypatch):
    ui, _, tiger, _ = fight
    tiger["legendary_resistances"] = 2
    _d20s(monkeypatch, 20, 20)
    ui._apply_custom_effect(CustomEffect(**FIREBALL, use_legendary_resistance=True))
    assert "legendary_resistances_left" not in tiger


def test_the_turn_column_sums_it_up(fight, monkeypatch):
    ui, *_ = fight
    _d20s(monkeypatch, 20, 1)
    ui._apply_custom_effect(CustomEffect(**FIREBALL, condition="Prone"))
    assert ui._action_result_label.text() == (
        "DC 15 DEX: 1 saved, 1 failed · 20 Fire · Prone"
    )


# ---------------------------------------------------------------------------
# The dialog


def _combo(dlg, name: str) -> QComboBox:
    return dlg.findChild(QComboBox, name)


def _apply(dlg):
    next(b for b in dlg.findChildren(QPushButton) if b.text() == "Apply").click()


def _chips(dlg, row: str) -> dict[str, QPushButton]:
    """A chip row's buttons, by their text without the & of a shortcut."""
    widget = dlg.findChild(QWidget, row)
    return {b.text().replace("&", ""): b for b in widget.findChildren(QPushButton)}


def _choose_roll(dlg, kind: str):
    """Click No roll, Saving throw or Attack roll, as the GM does."""
    _chips(dlg, "rollKindButtons")[kind].click()


def test_the_dialog_applies_all_of_it(fight, monkeypatch):
    ui, _, tiger, bandit = fight
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    assert dlg.windowTitle() == "Custom Effect"
    combo = _combo(dlg, "saveAbility")
    combo.setCurrentIndex(combo.findData("DEX"))
    dlg.findChild(QSpinBox, "saveDc").setValue(15)
    dlg.findChild(QLineEdit, "effectDamage").setText("20 fire")
    _combo(dlg, "conditionName").setCurrentText("Prone")
    _d20s(monkeypatch, 20, 1)
    _apply(dlg)
    assert tiger["hp"] == tiger["max_hp"] - 10
    assert "Prone" not in tiger["conditions"]
    assert bandit["hp"] == bandit["max_hp"] - 20
    assert "Prone" in bandit["conditions"]


def test_enter_in_the_damage_box_applies_once(fight, monkeypatch):
    ui, _, tiger, _ = fight
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    box = dlg.findChild(QLineEdit, "effectDamage")
    box.setText("6 fire")
    box.returnPressed.emit()
    box.returnPressed.emit()
    assert tiger["hp"] == tiger["max_hp"] - 6


@pytest.mark.parametrize(
    "damage, words",
    [("6", "needs a type"), ("6 zz", "isn't a damage type"), ("", "Add a saving")],
)
def test_the_dialog_says_whats_wrong_and_stays_open(fight, monkeypatch, damage, words):
    ui, _, tiger, _ = fight
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    dlg.findChild(QLineEdit, "effectDamage").setText(damage)
    _apply(dlg)
    assert tiger["hp"] == tiger["max_hp"]
    assert ui.history == []
    labels = [label.text() for label in dlg.findChildren(type(ui.selected_label))]
    assert any(words in text for text in labels), labels


def test_the_save_controls_wait_for_an_ability(fight, monkeypatch):
    ui, *_ = fight
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    dc = dlg.findChild(QSpinBox, "saveDc")
    assert not dc.isEnabled()
    combo = _combo(dlg, "saveAbility")
    combo.setCurrentIndex(combo.findData("WIS"))
    assert dc.isEnabled()


def test_the_dialog_remembers_the_last_save(fight, monkeypatch):
    ui, *_ = fight
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    combo = _combo(dlg, "saveAbility")
    combo.setCurrentIndex(combo.findData("WIS"))
    dlg.findChild(QSpinBox, "saveDc").setValue(17)
    dlg.findChild(QCheckBox, "halfOnSave").setChecked(False)
    dlg.findChild(QLineEdit, "effectDamage").setText("6 fire")
    _d20s(monkeypatch, 1, 1)
    _apply(dlg)

    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    assert _combo(dlg, "saveAbility").currentData() == "WIS"
    assert dlg.findChild(QSpinBox, "saveDc").value() == 17
    assert not dlg.findChild(QCheckBox, "halfOnSave").isChecked()


def test_the_dialog_fits_the_smallest_window(fight, monkeypatch):
    ui, *_ = fight
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    assert dlg.layout().totalHeightForWidth(dlg.width()) <= 600


def test_legendary_resistance_shows_only_when_a_target_has_any(fight, monkeypatch):
    ui, _, tiger, _ = fight
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _choose_roll(dlg, SAVING_THROW)
    box = dlg.findChild(QCheckBox, "useLegendaryResistance")
    assert not box.isVisibleTo(dlg)
    tiger["legendary_resistances"] = 3
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _choose_roll(dlg, SAVING_THROW)
    assert dlg.findChild(QCheckBox, "useLegendaryResistance").isVisibleTo(dlg)


@pytest.fixture
def paladin_fight(tmp_path):
    """Edmund, a player with spells, targeting himself and a Tiger."""
    ui = make_ui(tmp_path, [Tiger()], [Edmund().build()])
    edmund, tiger = ui.characters
    ui._initiative_inputs[id(edmund)].setText("15")
    ui._initiative_inputs[id(tiger)].setText("10")
    ui._start_combat()
    ui._select_target_character(edmund)
    ui._select_target_character(tiger, ctrl=True)
    return ui, edmund, tiger


def test_the_dc_starts_at_the_casters(paladin_fight, monkeypatch):
    ui, edmund, _ = paladin_fight
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    expected = edmund["_stat_block"].calculate_difficulty_class()
    assert dlg.findChild(QSpinBox, "saveDc").value() == expected


def _typed_total(dlg, name: str) -> QLineEdit:
    """The save total box of the target called `name`."""
    return next(
        box
        for box in dlg.findChildren(QLineEdit, "typedTotal")
        if box.accessibleName() == name
    )


def test_a_players_total_is_typed_in_the_dialog(paladin_fight, monkeypatch):
    ui, edmund, tiger = paladin_fight
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    combo = _combo(dlg, "saveAbility")
    combo.setCurrentIndex(combo.findData("WIS"))
    dlg.findChild(QSpinBox, "saveDc").setValue(15)
    dlg.findChild(QLineEdit, "effectDamage").setText("20 fire")
    total = _typed_total(dlg, "Edmund")
    total.setText("18")
    _d20s(monkeypatch, 1)  # only the Tiger rolls
    _apply(dlg)
    assert edmund["hp"] == edmund["max_hp"] - 10
    assert "rolled 18" in _log(ui)


def test_a_bad_typed_total_says_so(paladin_fight, monkeypatch):
    ui, edmund, _ = paladin_fight
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    combo = _combo(dlg, "saveAbility")
    combo.setCurrentIndex(combo.findData("WIS"))
    dlg.findChild(QLineEdit, "effectDamage").setText("20 fire")
    total = _typed_total(dlg, "Edmund")
    total.setText("abc")
    _apply(dlg)
    assert edmund["hp"] == edmund["max_hp"]


def test_known_save_dc():
    assert known_save_dc(None) is None
    assert known_save_dc({"name": "Tiger"}) is None
    text = "It casts using Wisdom (spell save DC 14):"
    assert (
        known_save_dc({"actions": [{"name": "Spellcasting", "description": text}]})
        == 14
    )


def test_a_monster_sources_dc_starts_from_its_spellcasting(fight, monkeypatch):
    ui, pirate, *_ = fight
    ui._select_character(pirate)
    pirate["actions"] = [
        {"name": "Spellcasting", "description": "Wisdom (spell save DC 16):"}
    ]
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    assert dlg.findChild(QSpinBox, "saveDc").value() == 16


# ---------------------------------------------------------------------------
# What the review found


@pytest.mark.parametrize(
    "scores, modifier", [({"DEX": 10, "CON": 10}, 0), ({"DEX": 8, "CON": 6}, -1)]
)
def test_low_scores_arent_read_as_modifiers(scores, modifier):
    """A Commoner has no score over 10: its saves were +10."""
    assert save_modifier({"Ability Scores": scores}, "DEX") == modifier


def test_a_players_condition_immunity_counts():
    class Sheet:
        def condition_immunities(self):
            return {Condition.FRIGHTENED: ["Aura"]}

    assert is_immune_to({"_stat_block": Sheet()}, "Frightened")
    assert not is_immune_to({"_stat_block": Sheet()}, "Prone")


def test_petrified_means_immune_to_poisoned():
    assert is_immune_to({"conditions": ["Petrified"]}, "Poisoned")


def test_petrified_means_resistance_to_all_damage(fight):
    ui, _, tiger, _ = fight
    tiger["conditions"].append("Petrified")
    ui._apply_custom_effect(CustomEffect(damage=[(20, FIRE)]))
    assert tiger["hp"] == tiger["max_hp"] - 10


def test_exhaustion_is_flagged_since_its_levels_arent_tracked(monkeypatch):
    _d20s(monkeypatch, 10)
    assert (
        "Exhaustion"
        in roll_save({"conditions": ["Exhaustion"]}, "DEX", 5, "Neutral").note
    )


def test_a_mark_counts_with_no_save_and_is_used_up(fight):
    ui, _, tiger, _ = fight
    ui._toggle_saved(tiger)
    ui._apply_custom_effect(CustomEffect(damage=[(20, FIRE)]))
    assert tiger["hp"] == tiger["max_hp"] - 10
    assert ui._saved_targets == []


def test_a_mark_gives_way_to_a_rolled_save_and_is_used_up(fight, monkeypatch):
    ui, _, tiger, _ = fight
    ui._toggle_saved(tiger)
    _d20s(monkeypatch, 1, 1)
    ui._apply_custom_effect(CustomEffect(**FIREBALL))
    assert tiger["hp"] == tiger["max_hp"] - 20
    assert ui._saved_targets == []


def test_a_condition_in_lower_case_is_the_real_one(fight, monkeypatch):
    ui, _, tiger, _ = fight
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _combo(dlg, "conditionName").setCurrentText("stunned")
    _apply(dlg)
    assert "Stunned" in tiger["conditions"]
    assert "stunned" not in tiger["conditions"]


@pytest.mark.parametrize(
    "condition, auto_fails",
    [("Stunned by the blast", True), ("Stunnedish", False)],
)
def test_a_longer_custom_name_counts_as_the_condition(condition, auto_fails):
    result = roll_save({"conditions": [condition]}, "DEX", 1, "Neutral")
    assert (result.total is None) is auto_fails


def test_the_dc_stays_while_the_source_does(paladin_fight, monkeypatch):
    ui, edmund, _ = paladin_fight
    ui._select_character(edmund)
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    combo = _combo(dlg, "saveAbility")
    combo.setCurrentIndex(combo.findData("DEX"))
    dlg.findChild(QSpinBox, "saveDc").setValue(19)
    dlg.findChild(QLineEdit, "effectDamage").setText("1 fire")
    _apply(dlg)
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    assert dlg.findChild(QSpinBox, "saveDc").value() == 19


def test_a_negative_total_can_be_typed(paladin_fight, monkeypatch):
    ui, edmund, _ = paladin_fight
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    combo = _combo(dlg, "saveAbility")
    combo.setCurrentIndex(combo.findData("WIS"))
    dlg.findChild(QLineEdit, "effectDamage").setText("20 fire")
    total = _typed_total(dlg, "Edmund")
    total.setText("-1")
    _d20s(monkeypatch, 1)
    _apply(dlg)
    assert "rolled -1" in _log(ui)


def test_only_dead_targets_says_so(fight):
    ui, _, tiger, bandit = fight
    tiger["hp"] = bandit["hp"] = 0
    ui._apply_custom_effect(CustomEffect(**FIREBALL))
    assert "every target is dead" in ui._status_label.text()
    assert ui._action_result_label.text() == ""
    assert ui.history == []


# ---------------------------------------------------------------------------
# The rest of what a spell needs


def _source_fight(fight):
    ui, pirate, tiger, bandit = fight
    ui._select_character(pirate)
    return ui, pirate, tiger, bandit


def test_the_damage_type_dropdown(fight, monkeypatch):
    ui, _, tiger, _ = fight
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    types = _combo(dlg, "damageType")
    types.setCurrentIndex(types.findData(FIRE))
    dlg.findChild(QLineEdit, "effectDamage").setText("6")
    _apply(dlg)
    assert tiger["hp"] == tiger["max_hp"] - 6
    assert "takes 6 Fire damage" in _log(ui)


def test_the_dropdown_starts_on_the_sources_type(fight, monkeypatch):
    ui, pirate, *_ = fight
    ui._select_character(pirate)
    pirate["_last_damage_type"] = FIRE
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    assert _combo(dlg, "damageType").currentData() == FIRE


def test_a_typed_type_shows_in_the_dropdown(fight, monkeypatch):
    ui, *_ = fight
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    dlg.findChild(QLineEdit, "effectDamage").setText("8d6 fi")
    assert _combo(dlg, "damageType").currentData() == FIRE


def test_the_type_used_is_remembered(fight):
    ui, pirate, *_ = fight
    ui._select_character(pirate)
    ui._apply_custom_effect(CustomEffect(damage=[(5, FIRE)]))
    assert pirate["_last_damage_type"] == FIRE


def test_the_name_goes_in_the_log_and_the_summary(fight, monkeypatch):
    ui, *_ = fight
    _d20s(monkeypatch, 1, 1)
    ui._apply_custom_effect(CustomEffect(**FIREBALL, name="Fireball"))
    assert "save against Fireball" in _log(ui)
    assert ui._action_result_label.text().startswith("Fireball · ")


def test_resistances_can_be_left_out(fight):
    ui, _, tiger, _ = fight
    tiger["damage_resistances"] = [DamageTypeEntry(damage_types=[DamageType.FIRE])]
    ui._apply_custom_effect(CustomEffect(damage=[(20, FIRE)], count_resistances=False))
    assert tiger["hp"] == tiger["max_hp"] - 20


def test_a_spell_slot_and_action_are_spent(fight):
    ui, pirate, *_ = _source_fight(fight)
    pirate["spell_slots"] = {3: 2}
    ui._apply_custom_effect(
        CustomEffect(damage=[(5, FIRE)], slot_level=3, action_cost="Action")
    )
    assert pirate["spell_slots"] == {3: 1}
    assert pirate["action_uses"] == {"Action": 1}


def test_the_dialog_offers_the_slots_left(fight, monkeypatch):
    ui, pirate, *_ = _source_fight(fight)
    pirate["spell_slots"] = {1: 0, 3: 2}
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    slots = _combo(dlg, "spellSlot")
    assert [slots.itemData(i) for i in range(slots.count())] == [None, 3]


def test_without_a_source_the_costs_are_off(fight, monkeypatch):
    ui, pirate, tiger, _ = fight
    ui.selected_character = None
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    assert not _combo(dlg, "spellSlot").isEnabled()
    assert not dlg.findChild(QCheckBox, "sourceConcentrates").isEnabled()


def test_a_slot_and_action_undo_with_the_effect(fight):
    ui, pirate, *_ = _source_fight(fight)
    pirate["spell_slots"] = {3: 2}
    ui._apply_custom_effect(
        CustomEffect(damage=[(5, FIRE)], slot_level=3, action_cost="Action")
    )
    ui._undo_last()
    assert pirate["spell_slots"] == {3: 2}
    assert not pirate.get("action_uses")
    assert ui.history == []


def _web(**kwargs):
    return CustomEffect(
        name="Web",
        condition="Restrained",
        duration={"seconds": 3600},
        concentration=True,
        **kwargs,
    )


def test_concentrating_marks_the_source(fight):
    ui, pirate, *_ = _source_fight(fight)
    ui._apply_custom_effect(_web())
    assert "Concentrating" in pirate["conditions"]
    (entry,) = pirate["active_spells"]
    assert (entry["name"], entry["concentration"]) == ("Web", True)
    assert entry["time_left"] == 3600


def test_losing_concentration_ends_the_condition_on_the_targets(fight):
    ui, pirate, tiger, bandit = _source_fight(fight)
    ui._apply_custom_effect(_web())
    assert "Restrained" in tiger["conditions"]
    ui._remove_condition_from(pirate, "Concentrating", source=pirate)
    assert "Restrained" not in tiger["conditions"]
    assert "Restrained" not in bandit["conditions"]


def test_only_those_who_failed_are_freed(fight, monkeypatch):
    ui, pirate, tiger, bandit = _source_fight(fight)
    _d20s(monkeypatch, 20, 1)
    ui._apply_custom_effect(_web(ability="DEX", dc=15))
    (entry,) = pirate["active_spells"]
    assert [a["condition"] for a in entry["applied"]] == ["Restrained"]
    assert "Restrained" in bandit["conditions"]
    ui._remove_condition_from(pirate, "Concentrating", source=pirate)
    assert "Restrained" not in bandit["conditions"]


def test_a_new_concentration_ends_the_old_effect(fight):
    ui, pirate, tiger, _ = _source_fight(fight)
    ui._apply_custom_effect(_web())
    ui._apply_custom_effect(
        CustomEffect(name="Bane", condition="Bane", concentration=True)
    )
    assert "Restrained" not in tiger["conditions"]
    assert "Bane" in tiger["conditions"]
    assert [e["name"] for e in pirate["active_spells"]] == ["Bane"]


def test_dismissing_the_effect_ends_it_on_the_targets(fight):
    ui, pirate, tiger, _ = _source_fight(fight)
    ui._apply_custom_effect(_web())
    ui._remove_active_spell(pirate, pirate["active_spells"][0])
    assert "Restrained" not in tiger["conditions"]
    assert "Concentrating" not in pirate["conditions"]


def test_a_cast_spells_badge_ends_with_its_concentration(fight):
    ui, pirate, tiger, _ = _source_fight(fight)
    ui._apply_cast_spell(SpellFactory.create("Hold Person"))
    assert "Hold Person" in tiger["conditions"]
    ui._remove_condition_from(pirate, "Concentrating", source=pirate)
    assert "Hold Person" not in tiger["conditions"]


def test_undo_brings_back_what_losing_concentration_ended(fight):
    ui, pirate, tiger, _ = _source_fight(fight)
    ui._apply_custom_effect(_web())
    ui._remove_condition_from(pirate, "Concentrating", source=pirate)
    ui._undo_last()
    assert "Restrained" in tiger["conditions"]
    assert pirate["active_spells"]


def _hold(**kwargs):
    return CustomEffect(
        name="Hold",
        condition="Paralyzed",
        ability="WIS",
        dc=15,
        repeat_save=True,
        **kwargs,
    )


def _to_end_of(ui, char):
    """Pass turns until char's has just ended."""
    while ui.initiative_order[ui.current_turn_idx] is not char:
        ui._advance_turn()
    ui._advance_turn()


def test_a_monster_repeats_its_save_as_its_turn_ends(fight, monkeypatch):
    ui, _, tiger, bandit = fight
    _d20s(monkeypatch, 1, 1)
    ui._apply_custom_effect(_hold())
    tiger["Saving Throws"] = {"WIS": 0}
    _d20s(monkeypatch, 15)
    ui._advance_turn()  # Tiger's turn starts
    assert "Paralyzed" in tiger["conditions"], "only the end of its turn counts"
    ui._advance_turn()  # ...and ends, on a 15
    assert "Paralyzed" not in tiger["conditions"]
    assert repeat_saves(tiger) == []
    assert "Tiger ends Paralyzed with a DC 15 Wisdom save" in _log(ui)


def test_a_failed_repeat_keeps_the_condition(fight, monkeypatch):
    ui, _, tiger, _ = fight
    _d20s(monkeypatch, 1, 1)
    ui._apply_custom_effect(_hold())
    tiger["Saving Throws"] = {"WIS": 0}
    _d20s(monkeypatch, 5)
    ui._advance_turn()
    ui._advance_turn()
    assert "Paralyzed" in tiger["conditions"]
    assert repeat_saves(tiger)
    ui._refresh_views()
    assert "failed" in ui._turn_reminders_label.text()


def test_a_player_gets_a_reminder_instead(fight, monkeypatch):
    ui, _, tiger, _ = fight
    tiger["_is_player"] = True
    _d20s(monkeypatch, 1, 1)
    ui._apply_custom_effect(_hold())
    ui._advance_turn()
    ui._advance_turn()
    ui._refresh_views()
    assert "Paralyzed" in tiger["conditions"]
    assert (
        "Tiger: DC 15 Wisdom save to end Paralyzed" in ui._turn_reminders_label.text()
    )


def test_a_condition_gone_ends_the_repeat(fight, monkeypatch):
    ui, _, tiger, _ = fight
    _d20s(monkeypatch, 1, 1)
    ui._apply_custom_effect(_hold())
    ui._remove_condition_from(tiger, "Paralyzed")
    ui._advance_turn()
    ui._advance_turn()
    assert repeat_saves(tiger) == []


def test_undoing_a_repeat_save_gets_the_same_roll(fight, monkeypatch):
    ui, _, tiger, _ = fight
    _d20s(monkeypatch, 1, 1)
    ui._apply_custom_effect(_hold())
    tiger["Saving Throws"] = {"WIS": 0}
    ui._advance_turn()
    rolls = iter([5, 5, 20, 20])
    monkeypatch.setattr(random, "randint", lambda low, high: next(rolls))
    ui._advance_turn()  # a 5: it stays
    assert "Paralyzed" in tiger["conditions"]
    ui._undo_last()
    ui._advance_turn()  # the same 5, not the 20
    assert "Paralyzed" in tiger["conditions"]


def test_the_dialog_applies_the_new_options(fight, monkeypatch):
    ui, pirate, tiger, _ = _source_fight(fight)
    pirate["spell_slots"] = {2: 1}
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    dlg.findChild(QLineEdit, "effectName").setText("Hold Person")
    combo = _combo(dlg, "saveAbility")
    combo.setCurrentIndex(combo.findData("WIS"))
    dlg.findChild(QSpinBox, "saveDc").setValue(15)
    dlg.findChild(QCheckBox, "repeatSave").setChecked(True)
    dlg.findChild(QCheckBox, "sourceConcentrates").setChecked(True)
    slots = _combo(dlg, "spellSlot")
    slots.setCurrentIndex(slots.findData(2))
    actions = _combo(dlg, "actionCost")
    actions.setCurrentIndex(actions.findData("Action"))
    _combo(dlg, "conditionName").setCurrentText("Paralyzed")
    _d20s(monkeypatch, 1, 1)
    _apply(dlg)
    assert "Paralyzed" in tiger["conditions"]
    assert repeat_saves(tiger)[0]["repeat_save"]["dc"] == 15
    assert pirate["spell_slots"] == {2: 0}
    assert pirate["action_uses"] == {"Action": 1}
    assert pirate["active_spells"][0]["name"] == "Hold Person"
    assert "Concentrating" in pirate["conditions"]


# ---------------------------------------------------------------------------
# What the review of concentration and repeat saves found


def test_a_players_reminder_survives_a_skipped_turn(tmp_path, monkeypatch):
    ui = make_ui(tmp_path, [Pirate(), Tiger(), _named(Pirate(), "Bandit")])
    pirate, tiger, bandit = ui.characters
    for char, value in zip(ui.characters, (15, 10, 5)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    pirate["_is_player"] = True
    ui._select_target_character(pirate)
    _d20s(monkeypatch, 1)
    ui._apply_custom_effect(_hold())
    tiger["hp"] = 0  # the turn right after the Pirate's is skipped
    ui._advance_turn()
    assert ui.initiative_order[ui.current_turn_idx] is bandit
    ui._refresh_views()
    assert "Pirate: DC 15 Wisdom save to end Paralyzed" in (
        ui._turn_reminders_label.text()
    )


def test_a_players_part_of_a_fight_survives_a_restart(tmp_path):
    ui = make_ui(tmp_path, [Tiger()], [Edmund().build()])
    edmund, tiger = ui.characters
    ui._initiative_inputs[id(edmund)].setText("15")
    ui._initiative_inputs[id(tiger)].setText("10")
    ui._start_combat()
    ui._select_character(edmund)
    ui._select_target_character(tiger)
    ui._apply_custom_effect(
        CustomEffect(
            name="Web", condition="Restrained", concentration=True, damage=[(1, FIRE)]
        )
    )
    ui._select_target_character(edmund)
    ui._add_custom_condition("Slowed", {"seconds": 60}, "Half speed")

    fresh = make_ui(tmp_path, [], [Edmund().build()])
    fresh._load_log_from_path(str(ui.log_file))
    loaded = next(c for c in fresh.characters if c.get("_is_player"))
    assert loaded["active_spells"][0]["name"] == "Web"
    assert timed_effects(loaded)[0]["name"] == "Slowed"
    assert _custom_notes(loaded) == {"Slowed": "Half speed"}


def _second_caster(ui, bandit):
    """Bandit becomes the source."""
    ui._select_character(bandit)


def test_a_condition_two_casters_gave_stays_until_both_end(fight):
    ui, pirate, tiger, bandit = _source_fight(fight)
    ui._set_targets([tiger])
    ui._apply_custom_effect(_web())
    _second_caster(ui, bandit)
    ui._apply_custom_effect(_web())
    ui._remove_condition_from(pirate, "Concentrating", source=pirate)
    assert "Restrained" in tiger["conditions"], "the Bandit still holds it"
    ui._remove_condition_from(bandit, "Concentrating", source=bandit)
    assert "Restrained" not in tiger["conditions"]


def test_two_casters_of_the_same_spell_share_its_badge(fight):
    ui, pirate, tiger, bandit = _source_fight(fight)
    ui._set_targets([tiger])
    ui._apply_cast_spell(SpellFactory.create("Hold Person"))
    _second_caster(ui, bandit)
    ui._apply_cast_spell(SpellFactory.create("Hold Person"))
    ui._remove_condition_from(pirate, "Concentrating", source=pirate)
    assert "Hold Person" in tiger["conditions"]


def test_a_condition_given_by_hand_outlasts_the_effect(fight):
    ui, pirate, tiger, _ = _source_fight(fight)
    tiger["conditions"].append("Restrained")
    ui._set_targets([tiger])
    ui._apply_custom_effect(_web())
    ui._remove_condition_from(pirate, "Concentrating", source=pirate)
    assert "Restrained" in tiger["conditions"]


def test_removing_and_regiving_by_hand_cuts_the_tie_to_the_effect(fight):
    ui, pirate, tiger, _ = _source_fight(fight)
    ui._set_targets([tiger])
    ui._apply_custom_effect(_web())
    ui._remove_condition_from(tiger, "Restrained")
    ui._add_condition_to(tiger, "Restrained")
    ui._remove_condition_from(pirate, "Concentrating", source=pirate)
    assert "Restrained" in tiger["conditions"]


def test_an_effect_ending_leaves_the_unconscious_of_0_hp(fight):
    ui, pirate, tiger, _ = _source_fight(fight)
    tiger["_is_player"] = True
    ui._set_targets([tiger])
    ui._apply_custom_effect(CustomEffect(condition="Unconscious", concentration=True))
    tiger["hp"] = 0
    ui._remove_condition_from(pirate, "Concentrating", source=pirate)
    assert "Unconscious" in tiger["conditions"]


def test_a_late_casters_round_lasts_a_round(fight):
    ui, _, tiger, bandit = fight
    ui._advance_turn()
    ui._advance_turn()  # the Bandit's turn, last in the round
    ui._select_character(bandit)
    ui._set_targets([tiger])
    ui._apply_custom_effect(
        CustomEffect(condition="Stunned", duration={"seconds": 6}, concentration=True)
    )
    ui._advance_turn()  # round 2
    assert "Stunned" in tiger["conditions"]
    ui._advance_turn()
    ui._advance_turn()  # the Bandit's turn again
    assert "Stunned" not in tiger["conditions"]
    assert "Concentrating" not in bandit["conditions"]


def test_a_cast_spell_counts_from_its_casters_turn(fight):
    ui, _, tiger, bandit = fight
    ui._advance_turn()
    ui._advance_turn()
    ui._select_character(bandit)
    ui._set_targets([tiger])
    ui._apply_cast_spell(SpellFactory.create("Hold Person"))
    (entry,) = bandit["active_spells"]
    time_left = entry["time_left"]
    ui._advance_turn()  # a new round, but not the Bandit's turn
    assert bandit["active_spells"][0]["time_left"] == time_left


def test_a_timer_that_doesnt_say_counts_at_the_round(fight):
    ui, pirate, *_ = fight
    pirate["active_spells"] = [
        {"name": "Old", "time_left": 60, "duration": 60, "concentration": False}
    ]
    ui._advance_turn()
    assert pirate["active_spells"][0]["time_left"] == 60
    ui._advance_turn()
    ui._advance_turn()  # round 2
    assert pirate["active_spells"][0]["time_left"] == 54


def test_a_turn_long_effect_ends_with_its_condition(fight):
    ui, pirate, tiger, _ = _source_fight(fight)
    ui._set_targets([tiger])
    ui._apply_custom_effect(
        CustomEffect(
            condition="Dazed",
            duration={"until": "end", "of": "source"},
            concentration=True,
        )
    )
    assert "Concentrating" in pirate["conditions"]
    ui._advance_turn()
    ui._advance_turn()
    ui._advance_turn()  # round 2, the Pirate's turn
    ui._advance_turn()  # ...and its end
    assert "Dazed" not in tiger["conditions"]
    assert "Concentrating" not in pirate["conditions"]
    assert not pirate["active_spells"]


def test_an_effect_that_ends_its_own_concentration_is_over(fight):
    ui, pirate, tiger, _ = _source_fight(fight)
    ui._set_targets([pirate, tiger])
    ui._apply_custom_effect(CustomEffect(condition="Stunned", concentration=True))
    assert "Concentrating" not in pirate["conditions"]
    assert not pirate.get("active_spells")
    assert "Stunned" not in tiger["conditions"]


def test_a_repeat_isnt_rolled_for_a_condition_ending_that_turn(fight, monkeypatch):
    ui, _, tiger, _ = fight
    _d20s(monkeypatch, 1, 1)
    ui._apply_custom_effect(
        CustomEffect(
            condition="Paralyzed",
            ability="WIS",
            dc=15,
            repeat_save=True,
            duration={"until": "end", "of": "target"},
        )
    )
    ui._advance_turn()
    _d20s(monkeypatch, 1)
    ui._advance_turn()  # the Tiger's turn ends, and the condition with it
    ui._refresh_views()
    assert "Paralyzed" not in tiger["conditions"]
    assert "Tiger failed" not in ui._turn_reminders_label.text()
    assert repeat_saves(tiger) == []


def test_a_condition_given_twice_repeats_once(fight, monkeypatch):
    ui, _, tiger, _ = fight
    _d20s(monkeypatch, 1, 1, 1, 1)
    ui._apply_custom_effect(_hold())
    ui._apply_custom_effect(_hold())
    assert len(repeat_saves(tiger)) == 1


def test_a_condition_removed_takes_its_repeat_save_with_it(fight, monkeypatch):
    ui, _, tiger, _ = fight
    _d20s(monkeypatch, 1, 1)
    ui._apply_custom_effect(_hold())
    ui._remove_condition_from(tiger, "Paralyzed")
    assert repeat_saves(tiger) == []


def test_a_repeat_keeps_the_rolls_mode(fight, monkeypatch):
    ui, _, tiger, _ = fight
    tiger["Saving Throws"] = {"WIS": 0}
    _d20s(monkeypatch, 1, 1)
    ui._apply_custom_effect(_hold(mode="Advantage"))
    assert repeat_saves(tiger)[0]["repeat_save"]["mode"] == "Advantage"
    ui._advance_turn()
    rolls = iter([3, 16])
    monkeypatch.setattr(random, "randint", lambda low, high: next(rolls))
    ui._advance_turn()
    assert "Paralyzed" not in tiger["conditions"], "16 on Advantage saves"


def test_a_repeat_can_spend_legendary_resistance(fight, monkeypatch):
    ui, _, tiger, _ = fight
    tiger.update({"Saving Throws": {"WIS": 0}, "legendary_resistances": 2})
    _d20s(monkeypatch, 1, 1)
    effect = _hold()
    ui._apply_custom_effect(effect)
    repeat_saves(tiger)[0]["repeat_save"]["use_legendary_resistance"] = True
    ui._advance_turn()
    _d20s(monkeypatch, 1)
    ui._advance_turn()
    assert "Paralyzed" not in tiger["conditions"]
    assert tiger["legendary_resistances_left"] == 1


def test_a_repeat_says_why_it_failed(fight, monkeypatch):
    ui, _, tiger, _ = fight
    _d20s(monkeypatch, 1, 1)
    ui._apply_custom_effect(
        CustomEffect(condition="Paralyzed", ability="DEX", dc=15, repeat_save=True)
    )
    ui._advance_turn()
    ui._advance_turn()
    assert "Paralyzed: automatic failure" in _log(ui)


def test_a_marked_target_avoids_the_condition_with_no_save(fight):
    ui, _, tiger, bandit = fight
    ui._toggle_saved(tiger)
    ui._apply_custom_effect(CustomEffect(damage=[(20, FIRE)], condition="Prone"))
    assert tiger["hp"] == tiger["max_hp"] - 10
    assert "Prone" not in tiger["conditions"]
    assert "Prone" in bandit["conditions"]


def test_a_second_combatant_of_a_name_is_numbered(fight):
    ui, *_ = fight
    ui._add_ad_hoc_combatant("Vine")
    ui._add_ad_hoc_combatant("Vine")
    ui._add_ad_hoc_combatant("Vine")
    assert [c["name"] for c in ui.characters[-3:]] == ["Vine", "Vine 2", "Vine 3"]


# ---------------------------------------------------------------------------
# An attack roll instead of a saving throw

BOLT = {"damage": [(20, FIRE)], "attack_bonus": 5}


@pytest.fixture
def armored(fight):
    """The fight with both targets at AC 15, so a +5 hits on a 10 or more."""
    _, _, tiger, bandit = fight
    tiger["ac"] = bandit["ac"] = 15
    return fight


@pytest.mark.parametrize(
    "d20, roll",
    [
        (12, AttackRoll(total=17)),
        (20, AttackRoll(natural=20)),
        (1, AttackRoll(natural=1)),
    ],
)
def test_roll_attack(monkeypatch, d20, roll):
    _d20s(monkeypatch, d20)
    assert roll_attack(5, "Neutral") == roll


@pytest.mark.parametrize("mode, total", [("Advantage", 17), ("Disadvantage", 4)])
def test_an_attacks_advantage(monkeypatch, mode, total):
    rolls = iter([4, 17])
    monkeypatch.setattr(random, "randint", lambda low, high: next(rolls))
    assert roll_attack(0, mode) == AttackRoll(total=total)


def test_a_critical_rolls_the_dice_twice_and_adds_modifiers_once(monkeypatch):
    monkeypatch.setattr(random, "randint", lambda low, high: 3)
    assert read_damage("2d6 + 3", FIRE, critical=True) == ([(15, FIRE)], "")
    assert read_damage("28 fi", critical=True) == ([(28, FIRE)], "")


def test_meeting_the_ac_hits_and_a_miss_takes_nothing(armored, monkeypatch):
    ui, _, tiger, bandit = armored
    _d20s(monkeypatch, 10, 9)
    ui._apply_custom_effect(CustomEffect(**BOLT))
    assert tiger["hp"] == tiger["max_hp"] - 20
    assert bandit["hp"] == bandit["max_hp"]
    assert "Pirate's attack roll of 15 hits Tiger" in _log(ui)
    assert "Pirate's attack roll of 14 misses Bandit" in _log(ui)


def test_a_condition_lands_only_on_a_hit(armored, monkeypatch):
    ui, _, tiger, bandit = armored
    _d20s(monkeypatch, 10, 9)
    ui._apply_custom_effect(CustomEffect(condition="Prone", attack_bonus=5))
    assert "Prone" in tiger["conditions"]
    assert "Prone" not in bandit["conditions"]


def test_cover_counts_against_the_attack(armored, monkeypatch):
    ui, _, tiger, _ = armored
    tiger["visibility_states"] = ["Half Cover"]
    _d20s(monkeypatch, 10, 10)
    ui._apply_custom_effect(CustomEffect(**BOLT))
    assert tiger["hp"] == tiger["max_hp"]


def test_a_natural_20_always_hits_and_is_critical(armored, monkeypatch):
    ui, _, tiger, _ = armored
    tiger["ac"] = 99
    _d20s(monkeypatch, 20, 1)
    ui._apply_custom_effect(CustomEffect(**BOLT, critical_damage=[(25, FIRE)]))
    assert tiger["hp"] == tiger["max_hp"] - 25
    assert "natural 20 hits Tiger (critical hit)" in _log(ui)


def test_a_natural_1_always_misses(armored, monkeypatch):
    ui, _, _, bandit = armored
    _d20s(monkeypatch, 20, 1)
    ui._apply_custom_effect(CustomEffect(damage=[(5, FIRE)], attack_bonus=99))
    assert bandit["hp"] == bandit["max_hp"]


def test_a_hit_that_isnt_critical_has_the_plain_damage(armored, monkeypatch):
    ui, _, tiger, _ = armored
    _d20s(monkeypatch, 10, 1)
    ui._apply_custom_effect(CustomEffect(**BOLT, critical_damage=[(25, FIRE)]))
    assert tiger["hp"] == tiger["max_hp"] - 20


def test_a_critical_with_no_dice_is_the_same_damage(armored, monkeypatch):
    ui, _, tiger, _ = armored
    _d20s(monkeypatch, 20, 1)
    ui._apply_custom_effect(CustomEffect(**BOLT))
    assert tiger["hp"] == tiger["max_hp"] - 20


def test_a_target_with_no_ac_counts_as_hit(armored, monkeypatch):
    ui, _, tiger, _ = armored
    tiger["ac"] = None
    _d20s(monkeypatch, 2, 2)
    ui._apply_custom_effect(CustomEffect(**BOLT))
    assert tiger["hp"] == tiger["max_hp"] - 20
    assert "Tiger has no AC to check" in ui._status_label.text()


@pytest.mark.parametrize("d20, taken", [(10, 20), (9, 0)])
def test_a_mark_gives_way_to_an_attack_and_is_used_up(armored, monkeypatch, d20, taken):
    ui, _, tiger, _ = armored
    ui._toggle_saved(tiger)
    _d20s(monkeypatch, d20, d20)
    ui._apply_custom_effect(CustomEffect(**BOLT))
    assert tiger["hp"] == tiger["max_hp"] - taken
    assert ui._saved_targets == []


def test_a_typed_attack_is_used(armored, monkeypatch):
    ui, _, tiger, bandit = armored
    _d20s(monkeypatch, 1)  # the Tiger's: the Bandit's roll is typed
    ui._apply_custom_effect(
        CustomEffect(**BOLT, typed_attacks={id(bandit): AttackRoll(total=15)})
    )
    assert tiger["hp"] == tiger["max_hp"]
    assert bandit["hp"] == bandit["max_hp"] - 20


def test_a_dead_target_isnt_attacked(armored, monkeypatch):
    ui, _, tiger, _ = armored
    tiger["hp"] = 0
    _d20s(monkeypatch, 10)  # only the Bandit is rolled for
    ui._apply_custom_effect(CustomEffect(**BOLT))
    assert "Tiger" not in ui._status_label.text()


def test_legendary_resistance_doesnt_stop_an_attack(armored, monkeypatch):
    ui, _, tiger, _ = armored
    tiger["legendary_resistances"] = 2
    _d20s(monkeypatch, 10, 10)
    ui._apply_custom_effect(CustomEffect(**BOLT, use_legendary_resistance=True))
    assert tiger["hp"] == tiger["max_hp"] - 20
    assert "legendary_resistances_left" not in tiger


def test_concentration_holds_only_who_was_hit(armored, monkeypatch):
    ui, pirate, _, _ = armored
    ui._select_character(pirate)
    _d20s(monkeypatch, 10, 9)
    ui._apply_custom_effect(
        CustomEffect(
            name="Vine", condition="Restrained", attack_bonus=5, concentration=True
        )
    )
    (spell,) = pirate["active_spells"]
    assert spell["applied"] == [{"target": "Tiger", "condition": "Restrained"}]


def test_an_attack_shows_the_players_what_it_showed_of_the_ac(armored, monkeypatch):
    ui, _, tiger, bandit = armored
    _d20s(monkeypatch, 10, 9)
    ui._apply_custom_effect(CustomEffect(**BOLT))
    assert tiger["ac_at_most"] == 15
    assert bandit["ac_above"] == 14


def test_a_hidden_attacker_shows_them_nothing(armored, monkeypatch):
    ui, pirate, tiger, _ = armored
    pirate["conditions"].append("Invisible")
    _d20s(monkeypatch, 10, 9)
    ui._apply_custom_effect(CustomEffect(**BOLT))
    assert "ac_at_most" not in tiger


def test_the_player_link_reads_a_hit_with_its_damage(armored, monkeypatch):
    ui, *_ = armored
    _d20s(monkeypatch, 12, 2)
    ui._apply_custom_effect(
        CustomEffect(damage=[(5, FIRE)], attack_bonus=5, name="Fire Bolt")
    )
    (round_log,) = ui._public_log()
    (turn,) = round_log["turns"]
    assert turn["lines"] == [
        {"kind": "other", "text": "Pirate uses Fire Bolt", "amount": ""},
        {"kind": "hit", "text": "Hits Tiger (17)", "amount": "5 Fire"},
        {"kind": "miss", "text": "Misses Bandit (Pirate) (7)", "amount": ""},
    ]


def test_an_attack_is_one_undo(armored, monkeypatch):
    ui, _, tiger, bandit = armored
    _d20s(monkeypatch, 10, 9)
    ui._apply_custom_effect(CustomEffect(**BOLT, condition="Prone"))
    ui._undo_last()
    assert tiger["hp"] == tiger["max_hp"]
    assert "Prone" not in tiger["conditions"]
    assert "ac_at_most" not in tiger
    assert "ac_above" not in bandit
    assert "attack roll" not in _log(ui)


def test_the_turn_column_and_status_sum_up_an_attack(armored, monkeypatch):
    ui, *_ = armored
    _d20s(monkeypatch, 10, 9)
    ui._apply_custom_effect(CustomEffect(**BOLT, condition="Prone"))
    assert ui._action_result_label.text() == (
        "Attack: 1 hit, 1 missed · 20 Fire · Prone"
    )
    assert ui._status_label.text() == (
        "Tiger: 15 vs AC 15, hit; Bandit (Pirate): 14 vs AC 15, miss"
    )


def test_known_attack_bonus():
    assert known_attack_bonus(None) is None
    assert known_attack_bonus({"name": "Tiger"}) is None
    casting = "using Wisdom (spell save DC 14, +6 to hit with spell attacks):"
    bite = "Melee Attack Roll: +7, reach 5 ft. Hit: 7 (1d8 + 3) Piercing damage."
    spellcasting = {"name": "Spellcasting", "description": casting}
    claws = {"name": "Bite", "description": bite}
    assert known_attack_bonus({"actions": [spellcasting]}) == 6
    assert known_attack_bonus({"actions": [claws]}) == 7
    assert known_attack_bonus({"actions": [claws, spellcasting]}) == 6
    assert known_attack_bonus({"traits": [spellcasting]}) == 6


def test_a_player_with_no_spellcasting_has_no_attack_bonus():
    class NoCaster:
        spell_casting_ability = None

    assert known_attack_bonus({"_stat_block": NoCaster()}) is None


def _attack_dialog(ui, monkeypatch):
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _combo(dlg, "rollKind").setCurrentText(ATTACK_ROLL)
    return dlg


def test_the_dialog_asks_for_a_bonus_instead_of_a_dc(fight, monkeypatch):
    ui, *_ = fight
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _choose_roll(dlg, SAVING_THROW)
    dc = dlg.findChild(QSpinBox, "saveDc")
    bonus = dlg.findChild(QSpinBox, "attackBonus")
    abilities = dlg.findChild(QWidget, "saveAbilityButtons")

    def labels() -> list[str]:
        return [label.text() for label in dlg.findChildren(type(ui.selected_label))]

    assert dc.isVisibleTo(dlg) and abilities.isVisibleTo(dlg)
    assert not bonus.isVisibleTo(dlg)
    assert "Condition (on a failed save)" in labels()

    _combo(dlg, "rollKind").setCurrentText(ATTACK_ROLL)
    assert bonus.isVisibleTo(dlg)
    assert not dc.isVisibleTo(dlg) and not abilities.isVisibleTo(dlg)
    assert _combo(dlg, "saveMode").isEnabled()
    assert "Condition (on a hit)" in labels()


def test_the_save_only_ticks_go_away_for_an_attack(fight, monkeypatch):
    ui, _, tiger, _ = fight
    tiger["legendary_resistances"] = 3
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _choose_roll(dlg, SAVING_THROW)
    boxes = [
        dlg.findChild(QCheckBox, name)
        for name in ("halfOnSave", "repeatSave", "useLegendaryResistance")
    ]
    assert all(box.isVisibleTo(dlg) for box in boxes)
    _combo(dlg, "rollKind").setCurrentText(ATTACK_ROLL)
    assert not any(box.isVisibleTo(dlg) for box in boxes)
    _combo(dlg, "rollKind").setCurrentText("Saving throw")
    assert all(box.isVisibleTo(dlg) for box in boxes)


# The roll chips: No roll, Saving throw and Attack roll, one click apart


def test_no_roll_hides_both_rolls_controls(fight, monkeypatch):
    ui, *_ = fight
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _choose_roll(dlg, "No roll")
    assert _combo(dlg, "saveAbility").currentData() is None
    assert _combo(dlg, "rollKind").currentText() == SAVING_THROW
    for name in ("saveDc", "attackBonus"):
        assert not dlg.findChild(QSpinBox, name).isVisibleTo(dlg), name
    for name in ("halfOnSave", "repeatSave"):
        assert not dlg.findChild(QCheckBox, name).isVisibleTo(dlg), name
    assert not dlg.findChild(QWidget, "saveModeButtons").isVisibleTo(dlg)
    assert not any(
        b.isVisibleTo(dlg) for b in dlg.findChildren(QLineEdit, "typedTotal")
    )
    labels = [label.text() for label in dlg.findChildren(QLabel)]
    assert "Condition" in labels


def test_the_roll_chip_shows_the_roll(fight, monkeypatch):
    ui, *_ = fight
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    chips = _chips(dlg, "rollKindButtons")

    def checked() -> list[str]:
        return [text for text, chip in chips.items() if chip.isChecked()]

    _choose_roll(dlg, ATTACK_ROLL)
    assert checked() == [ATTACK_ROLL]
    _combo(dlg, "rollKind").setCurrentText(SAVING_THROW)  # a pick sets the combos
    combo = _combo(dlg, "saveAbility")
    combo.setCurrentIndex(combo.findData("WIS"))
    assert checked() == [SAVING_THROW]
    _choose_roll(dlg, "No roll")
    assert checked() == ["No roll"]
    _chips(dlg, "rollKindButtons")["No roll"].click()  # clicked again: stays
    assert checked() == ["No roll"]


def test_a_saving_throw_after_no_roll_goes_back_to_its_ability(fight, monkeypatch):
    ui, *_ = fight
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _chips(dlg, "saveAbilityButtons")["WIS"].click()
    _choose_roll(dlg, "No roll")
    _choose_roll(dlg, SAVING_THROW)
    assert _combo(dlg, "saveAbility").currentData() == "WIS"


def test_a_saving_throw_starts_on_dexterity(fight, monkeypatch):
    ui, *_ = fight
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _choose_roll(dlg, SAVING_THROW)
    assert _combo(dlg, "saveAbility").currentData() == "DEX"


def test_an_ability_chip_makes_it_a_saving_throw(fight, monkeypatch):
    ui, *_ = fight
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _choose_roll(dlg, "No roll")
    _chips(dlg, "saveAbilityButtons")["CON"].click()
    assert _combo(dlg, "saveAbility").currentData() == "CON"
    assert _chips(dlg, "rollKindButtons")[SAVING_THROW].isChecked()
    assert dlg.findChild(QSpinBox, "saveDc").isVisibleTo(dlg)


def test_an_attack_keeps_the_ability_for_a_save_after(fight, monkeypatch):
    ui, *_ = fight
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _chips(dlg, "saveAbilityButtons")["INT"].click()
    _choose_roll(dlg, ATTACK_ROLL)
    _choose_roll(dlg, SAVING_THROW)
    assert _combo(dlg, "saveAbility").currentData() == "INT"


def test_the_mode_and_action_chips_set_their_values(fight, monkeypatch):
    ui, pirate, *_ = fight
    ui._select_character(pirate)
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _chips(dlg, "saveModeButtons")["Advantage"].click()  # no roll: nothing to
    assert _combo(dlg, "saveMode").currentText() == "Neutral"
    _choose_roll(dlg, SAVING_THROW)
    _chips(dlg, "saveModeButtons")["Advantage"].click()
    assert _combo(dlg, "saveMode").currentText() == "Advantage"
    _chips(dlg, "actionCostButtons")["Bonus Action"].click()
    assert _combo(dlg, "actionCost").currentData() == "Bonus Action"
    _combo(dlg, "actionCost").setCurrentIndex(0)
    assert _chips(dlg, "actionCostButtons")["None"].isChecked()


def test_the_cost_chips_wait_for_a_source(fight, monkeypatch):
    ui, *_ = fight
    ui.selected_character = None
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    assert not dlg.findChild(QWidget, "actionCostButtons").isEnabled()


def test_each_target_shows_its_save_bonus_and_ac(fight, monkeypatch):
    ui, _, tiger, bandit = fight
    bandit["visibility_states"] = [Visibility.HALF_COVER.value]
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)

    def infos() -> list[str]:
        rows = dlg.findChildren(QLabel, "targetRowInfo")
        return [label.text() for label in rows if label.isVisibleTo(dlg)]

    _chips(dlg, "saveAbilityButtons")["DEX"].click()
    # Both have +3 to Dexterity saves; Half Cover gives the Bandit "+2 bonus
    # to AC and Dexterity saving throws" (Rules Glossary, Cover; DI-066).
    assert infos() == ["DEX +3", "DEX +5 (cover)"]
    _chips(dlg, "saveAbilityButtons")["STR"].click()
    assert infos() == ["STR +3", "STR +0"]  # their Strength modifiers: 17, 10
    _choose_roll(dlg, ATTACK_ROLL)
    # Half cover adds 2 to the Bandit's AC.
    assert infos() == [f"AC {tiger['ac']}", f"AC {bandit['ac'] + 2} (cover)"]


def test_the_preview_says_what_apply_will_do(fight, monkeypatch):
    ui, pirate, *_ = fight
    ui._select_character(pirate)
    # Nothing in the preview is rolled: a die would fail the test.
    monkeypatch.setattr(random, "randint", lambda *a: pytest.fail("rolled"))
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _chips(dlg, "saveAbilityButtons")["DEX"].click()
    dlg.findChild(QSpinBox, "saveDc").setValue(15)
    dlg.findChild(QLineEdit, "effectDamage").setText("8d6")
    _combo(dlg, "damageType").setCurrentIndex(_combo(dlg, "damageType").findData(FIRE))
    _combo(dlg, "conditionName").setCurrentText("Prone")
    _chips(dlg, "actionCostButtons")["Action"].click()
    preview = dlg.findChild(QLabel, "effectPreview").text()
    assert preview == (
        "On 2 targets: DC 15 Dexterity save · 8d6 Fire, half on a save · Prone"
        " · costs Action"
    )


def test_the_preview_of_an_attack(fight, monkeypatch):
    ui, *_ = fight
    dlg = _attack_dialog(ui, monkeypatch)
    dlg.findChild(QSpinBox, "attackBonus").setValue(5)
    _chips(dlg, "saveModeButtons")["Disadvantage"].click()
    dlg.findChild(QLineEdit, "effectDamage").setText("2d6 fire")
    preview = dlg.findChild(QLabel, "effectPreview").text()
    assert preview == "On 2 targets: Attack +5 vs AC with Disadvantage · 2d6 fire"


def test_legendary_resistance_stays_away_with_none_left_after_an_attack(
    fight, monkeypatch
):
    ui, *_ = fight
    dlg = _attack_dialog(ui, monkeypatch)
    _combo(dlg, "rollKind").setCurrentText("Saving throw")
    box = dlg.findChild(QCheckBox, "useLegendaryResistance")
    assert not box.isVisibleTo(dlg)


def test_a_hidden_tick_doesnt_carry_over_to_an_attack(armored, monkeypatch):
    ui, _, tiger, _ = armored
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    dlg.findChild(QCheckBox, "repeatSave").setChecked(True)
    _combo(dlg, "rollKind").setCurrentText(ATTACK_ROLL)
    dlg.findChild(QSpinBox, "attackBonus").setValue(5)
    _combo(dlg, "conditionName").setCurrentText("Prone")
    _d20s(monkeypatch, 10, 10)
    _apply(dlg)
    assert "Prone" in tiger["conditions"]
    assert repeat_saves(tiger) == []


def test_the_dialog_applies_an_attack(armored, monkeypatch):
    ui, _, tiger, bandit = armored
    dlg = _attack_dialog(ui, monkeypatch)
    dlg.findChild(QSpinBox, "attackBonus").setValue(5)
    dlg.findChild(QLineEdit, "effectDamage").setText("20 fire")
    _combo(dlg, "conditionName").setCurrentText("Prone")
    _d20s(monkeypatch, 10, 9)
    _apply(dlg)
    assert tiger["hp"] == tiger["max_hp"] - 20
    assert "Prone" in tiger["conditions"]
    assert bandit["hp"] == bandit["max_hp"]
    assert "attack roll of 15 hits Tiger" in _log(ui)


def test_the_dialogs_attack_rolls_more_dice_on_a_critical(armored, monkeypatch):
    ui, _, tiger, _ = armored
    dlg = _attack_dialog(ui, monkeypatch)
    dlg.findChild(QLineEdit, "effectDamage").setText("2d6 + 3 fire")
    monkeypatch.setattr(random, "randint", lambda low, high: 20 if high == 20 else 3)
    _apply(dlg)
    assert tiger["hp"] == tiger["max_hp"] - 15


def test_an_attack_needs_nothing_else(armored, monkeypatch):
    ui, *_ = armored
    dlg = _attack_dialog(ui, monkeypatch)
    _d20s(monkeypatch, 10, 9)
    _apply(dlg)
    assert "attack roll" in _log(ui)


def test_the_dialog_remembers_the_attack(armored, monkeypatch):
    ui, *_ = armored
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    ability = _combo(dlg, "saveAbility")
    ability.setCurrentIndex(ability.findData("WIS"))
    _combo(dlg, "rollKind").setCurrentText(ATTACK_ROLL)
    dlg.findChild(QSpinBox, "attackBonus").setValue(7)
    _d20s(monkeypatch, 1, 1)
    _apply(dlg)

    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    assert _combo(dlg, "rollKind").currentText() == ATTACK_ROLL
    assert dlg.findChild(QSpinBox, "attackBonus").value() == 7
    assert dlg.findChild(QSpinBox, "attackBonus").isVisibleTo(dlg)
    assert _combo(dlg, "saveAbility").currentData() == "WIS"


def test_the_dialog_fits_the_smallest_window_for_an_attack(fight, monkeypatch):
    ui, *_ = fight
    dlg = _attack_dialog(ui, monkeypatch)
    assert dlg.layout().totalHeightForWidth(dlg.width()) <= 600


def test_the_bonus_starts_at_a_monsters_attack(fight, monkeypatch):
    ui, pirate, *_ = fight
    ui._select_character(pirate)
    pirate["actions"] = [
        {"name": "Slash", "description": "Melee Attack Roll: +6, reach 5 ft."}
    ]
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    assert dlg.findChild(QSpinBox, "attackBonus").value() == 6


def test_a_negative_bonus_starts_as_it_is(fight, monkeypatch):
    ui, pirate, *_ = fight
    ui._select_character(pirate)
    pirate["actions"] = [
        {"name": "Slap", "description": "Melee Attack Roll: -1, reach 5 ft."}
    ]
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    assert dlg.findChild(QSpinBox, "attackBonus").value() == -1


def test_the_bonus_starts_at_the_casters(paladin_fight, monkeypatch):
    ui, edmund, _ = paladin_fight
    ui._select_character(edmund)
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    expected = edmund["_stat_block"].calculate_attack_bonus()
    assert dlg.findChild(QSpinBox, "attackBonus").value() == expected


def test_a_player_attacking_types_a_roll_for_each_target(paladin_fight, monkeypatch):
    ui, edmund, tiger = paladin_fight
    tiger["ac"] = 15
    ui._select_character(edmund)
    dlg = _attack_dialog(ui, monkeypatch)
    dlg.findChild(QLineEdit, "effectDamage").setText("2d6 fire")
    first, second = dlg.findChildren(QLineEdit, "typedAttack")
    assert first.isVisibleTo(dlg)
    assert not dlg.findChild(QLineEdit, "typedTotal").isVisibleTo(dlg)
    first.setText("1")  # Edmund's
    second.setText("nat 20")  # the Tiger's
    monkeypatch.setattr(random, "randint", lambda low, high: 3)
    _apply(dlg)
    assert tiger["hp"] == tiger["max_hp"] - 12


def test_any_sources_roll_can_be_typed(armored, monkeypatch):
    """A player's summon isn't a player, but they roll for it at the table."""
    ui, _, tiger, bandit = armored
    dlg = _attack_dialog(ui, monkeypatch)
    dlg.findChild(QLineEdit, "effectDamage").setText("20 fire")
    first, second = dlg.findChildren(QLineEdit, "typedAttack")
    first.setText("15")
    _d20s(monkeypatch, 1)  # second is blank, so the Bandit's is rolled
    _apply(dlg)
    assert second.text() == ""
    assert tiger["hp"] == tiger["max_hp"] - 20
    assert bandit["hp"] == bandit["max_hp"]


def test_a_typed_attack_is_the_total_with_the_bonus_in_it(armored, monkeypatch):
    ui, _, tiger, _ = armored
    dlg = _attack_dialog(ui, monkeypatch)
    dlg.findChild(QSpinBox, "attackBonus").setValue(5)
    dlg.findChild(QLineEdit, "effectDamage").setText("20 fire")
    dlg.findChildren(QLineEdit, "typedAttack")[0].setText("14")
    _d20s(monkeypatch, 1)
    _apply(dlg)
    assert tiger["hp"] == tiger["max_hp"]
    assert "attack roll of 14 misses Tiger" in _log(ui)


def test_enter_in_a_typed_attack_applies(armored, monkeypatch):
    ui, _, tiger, _ = armored
    dlg = _attack_dialog(ui, monkeypatch)
    dlg.findChild(QLineEdit, "effectDamage").setText("20 fire")
    box = dlg.findChildren(QLineEdit, "typedAttack")[0]
    box.setText("nat 20")
    _d20s(monkeypatch, 1)
    box.returnPressed.emit()
    assert tiger["hp"] == tiger["max_hp"] - 20
    assert "natural 20 hits Tiger (critical hit)" in _log(ui)


def test_the_typed_attacks_wait_for_an_attack_roll(armored, monkeypatch):
    ui, *_ = armored
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    box = dlg.findChildren(QLineEdit, "typedAttack")[0]
    assert not box.isVisibleTo(dlg)
    _combo(dlg, "rollKind").setCurrentText(ATTACK_ROLL)
    assert box.isVisibleTo(dlg)


def test_a_bad_typed_attack_says_so(paladin_fight, monkeypatch):
    ui, edmund, tiger = paladin_fight
    ui._select_character(edmund)
    dlg = _attack_dialog(ui, monkeypatch)
    dlg.findChild(QLineEdit, "effectDamage").setText("20 fire")
    dlg.findChildren(QLineEdit, "typedAttack")[0].setText("abc")
    _apply(dlg)
    assert tiger["hp"] == tiger["max_hp"]
    assert ui.history == []
    labels = [label.text() for label in dlg.findChildren(type(ui.selected_label))]
    assert any("isn't an attack roll" in text for text in labels), labels


# ---------------------------------------------------------------------------
# Picking what was used (effect_options.py): it fills in the form, and Apply
# spends it as Cast Spell, Enable Feature and the turn column's buttons do.

SCIMITAR = {
    "name": "Scimitar",
    "description": "Melee Attack Roll: +4, reach 5 ft. Hit: 5 (1d6 + 2) Slashing damage.",
}
BREATH = {
    "name": "Fire Breath (Recharge 5–6)",
    "description": "Dexterity Saving Throw: DC 13, each creature in a 15-foot Cone."
    " Failure: 14 (4d6) Fire damage. Success: Half damage.",
}
REND = {
    "name": "Rend (Recharge 6)",
    "description": "Melee Attack Roll: +6, reach 5 ft. Hit: 9 (2d6 + 2) Slashing"
    " damage, and the target can't take Reactions until the start of its next turn"
    " while it's bleeding badly from the wound the claws leave in it.",
}
GAZE = {
    "name": "Gaze (Costs 2 Actions)",
    "description": "Wisdom Saving Throw: DC 14, one creature. Failure: The target has"
    " the Frightened condition, and it repeats the save at the end of each of its turns.",
}


def _tree(dlg) -> QTreeWidget:
    return dlg.findChild(QTreeWidget, "effectOptions")


def _rows(dlg) -> list[QTreeWidgetItem]:
    tree = _tree(dlg)
    return [
        tree.topLevelItem(i).child(j)
        for i in range(tree.topLevelItemCount())
        for j in range(tree.topLevelItem(i).childCount())
    ]


def _row(dlg, name: str) -> QTreeWidgetItem:
    return next(
        row for row in _rows(dlg) if row.data(0, Qt.ItemDataRole.UserRole).name == name
    )


def _pick(dlg, name: str):
    _tree(dlg).setCurrentItem(_row(dlg, name))


def _search(dlg) -> QLineEdit:
    return dlg.findChild(QLineEdit, "effectSearch")


def _form(dlg) -> dict:
    """What the form holds now."""
    return {
        "name": dlg.findChild(QLineEdit, "effectName").text(),
        "roll": _combo(dlg, "rollKind").currentText(),
        "ability": _combo(dlg, "saveAbility").currentData(),
        "dc": dlg.findChild(QSpinBox, "saveDc").value(),
        "bonus": dlg.findChild(QSpinBox, "attackBonus").value(),
        "half": dlg.findChild(QCheckBox, "halfOnSave").isChecked(),
        "repeat": dlg.findChild(QCheckBox, "repeatSave").isChecked(),
        "damage": dlg.findChild(QLineEdit, "effectDamage").text(),
        "type": _combo(dlg, "damageType").currentData(),
        "condition": _combo(dlg, "conditionName").currentText(),
        "duration": _combo(dlg, "conditionDuration").currentData(),
        "slot": _combo(dlg, "spellSlot").currentData(),
        "action": _combo(dlg, "actionCost").currentData(),
        "concentrates": dlg.findChild(QCheckBox, "sourceConcentrates").isChecked(),
        "note": dlg.findChild(QLabel, "effectNote").text(),
    }


@pytest.fixture
def monster(fight):
    """The Pirate, the source, with a stat block's actions, targeting the Tiger."""
    ui, pirate, tiger, bandit = _source_fight(fight)
    pirate.update(actions=[SCIMITAR, BREATH, REND], legendary_actions=[GAZE])
    ui._select_target_character(tiger)
    ui._refresh_views()
    return ui, pirate, tiger


@pytest.fixture
def paladin(paladin_fight):
    """Edmund, the source, targeting only the Tiger."""
    ui, edmund, tiger = paladin_fight
    ui._select_character(edmund)
    ui._select_target_character(tiger)
    return ui, edmund, tiger


def test_the_dialog_opens_on_the_search_box(paladin, monkeypatch):
    ui, *_ = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    assert dlg.focusWidget() is _search(dlg)
    assert dlg.findChild(QLabel, "effectNote").text() == ""


def test_the_categories(paladin, monkeypatch):
    ui, *_ = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    tree = _tree(dlg)
    categories = [tree.topLevelItem(i) for i in range(tree.topLevelItemCount())]
    assert [c.text(0) for c in categories] == [
        "Attacks",
        "Edmund's Spells",
        "Features",
        "All spells",
    ]
    # Only All spells is long enough to start folded.
    assert [c.isExpanded() for c in categories] == [True, True, True, False]


def _browsable(dlg) -> list[QTreeWidgetItem]:
    """The rows Up and Down go through: those of unfolded categories."""
    return [
        row
        for row in _rows(dlg)
        if row.parent().isExpanded() and not row.isHidden() and not row.isDisabled()
    ]


def test_down_and_up_from_the_search_box_pick_as_they_go(paladin, monkeypatch):
    ui, *_ = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    first, second = _browsable(dlg)[:2]
    QTest.keyClick(_search(dlg), Qt.Key.Key_Down)
    assert _tree(dlg).currentItem() is first
    assert _form(dlg)["name"] == first.data(0, Qt.ItemDataRole.UserRole).name
    QTest.keyClick(_search(dlg), Qt.Key.Key_Down)
    assert _tree(dlg).currentItem() is second
    assert _form(dlg)["name"] == second.data(0, Qt.ItemDataRole.UserRole).name
    QTest.keyClick(_search(dlg), Qt.Key.Key_Up)
    assert _tree(dlg).currentItem() is first
    assert dlg.focusWidget() is _search(dlg)  # still typing


def test_down_stops_at_the_last_row_it_can_show(paladin, monkeypatch):
    ui, *_ = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    rows = _browsable(dlg)
    for _ in range(len(rows) + 3):
        QTest.keyClick(_search(dlg), Qt.Key.Key_Down)
    # The last of Edmund's features: All spells is folded.
    assert _tree(dlg).currentItem() is rows[-1]
    assert rows[-1].parent().text(0) == "Features"


def test_down_goes_through_the_search_results(paladin, monkeypatch):
    ui, *_ = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _search(dlg).setText("fireball")
    QTest.keyClick(_search(dlg), Qt.Key.Key_Down)
    QTest.keyClick(_search(dlg), Qt.Key.Key_Down)
    assert _form(dlg)["name"] == "Delayed Blast Fireball"


def test_enter_applies_the_row_reached_with_the_arrows(paladin, monkeypatch):
    answer_out_of_resources(monkeypatch)  # Edmund has no slot for the spell picked.
    ui, edmund, tiger = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _search(dlg).setText("hold person")
    QTest.keyClick(_search(dlg), Qt.Key.Key_Down)
    assert _form(dlg)["name"] == "Hold Person"
    _search(dlg).returnPressed.emit()
    assert dlg.result() == QDialog.DialogCode.Accepted
    assert ui.history  # applied


def test_escape_empties_the_search_before_it_closes(paladin, monkeypatch):
    ui, *_ = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    rejected = []
    dlg.rejected.connect(lambda: rejected.append(True))
    _search(dlg).setText("fire")
    QTest.keyClick(_search(dlg), Qt.Key.Key_Escape)
    assert _search(dlg).text() == ""
    assert not rejected
    assert not _tree(dlg).topLevelItem(2).isHidden()  # the filter is gone


def test_typing_in_the_list_types_in_the_search_box(paladin, monkeypatch):
    ui, *_ = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _tree(dlg).setFocus()
    QTest.keyClicks(_tree(dlg), "bles")
    assert _search(dlg).text() == "bles"


def test_ctrl_enter_applies_from_anywhere(fight, monkeypatch):
    ui, _, tiger, _ = fight
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    dlg.findChild(QLineEdit, "effectDamage").setText("6 fire")
    shortcut = next(
        s for s in dlg.findChildren(QShortcut) if s.key().toString() == "Ctrl+Return"
    )
    shortcut.activated.emit()
    assert tiger["hp"] == tiger["max_hp"] - 6


def test_the_details_show_the_picks_rules_text(paladin, monkeypatch):
    ui, *_ = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    details = dlg.findChild(QTextBrowser, "effectDetails")
    assert "Enter" in details.toPlainText()  # how to use it, before a pick
    _search(dlg).setText("hold person")
    _search(dlg).returnPressed.emit()
    text = details.toPlainText()
    assert text.startswith("Hold Person")
    assert "Paralyzed condition" in text
    dlg.findChild(QLineEdit, "effectName").textEdited.emit("My own")
    assert "Enter" in details.toPlainText()  # the pick was dropped


def test_a_row_shows_its_numbers_in_their_own_column(monster, monkeypatch):
    ui, *_ = monster
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    row = _row(dlg, "Scimitar")
    assert (row.text(0), row.text(1)) == ("Scimitar", "+4  1d6 + 2 Slashing")


# A picked spell's, feature's or action's badge can be clicked to read it, as
# Cast Spell's can


def _badge(ui, char: dict, name: str):
    """The clickable badge for condition `name` on char's card, or None."""
    card = ui._card_widgets[id(char)]
    return next((b for b in card.findChildren(QPushButton) if b.text() == name), None)


def _clicked_popup(ui, monkeypatch, char: dict, name: str) -> tuple[str, str]:
    """(heading, body) of the popup clicking char's `name` badge opens."""
    shown = []
    monkeypatch.setattr(
        ui,
        "_show_rule_popup",
        lambda title, heading, body: shown.append((heading, body)),
    )
    badge = _badge(ui, char, name)
    assert badge is not None, f"no clickable {name} badge"
    badge.click()
    assert len(shown) == 1, shown
    return shown[0]


def _apply_guidance(ui, monkeypatch, notes: str = ""):
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _search(dlg).setText("guidance")
    _search(dlg).returnPressed.emit()
    assert _form(dlg)["condition"] == "Guidance"
    dlg.findChild(QLineEdit, "conditionNotes").setText(notes)
    _apply(dlg)


def test_a_picked_spells_badge_shows_the_spell(paladin, monkeypatch):
    ui, _, tiger = paladin
    _apply_guidance(ui, monkeypatch)
    assert "Guidance" in tiger["conditions"]
    heading, body = _clicked_popup(ui, monkeypatch, tiger, "Guidance")
    assert heading == "Guidance"
    guidance = SpellFactory.create("Guidance")
    assert guidance.description.split("\n")[0] in body
    assert "<b>Duration:</b>" in body  # the spell's card, as Cast Spell's
    assert _badge(ui, tiger, "Guidance").toolTip() == body


def test_a_picked_spells_badge_has_the_schools_color(paladin, monkeypatch):
    ui, _, tiger = paladin
    _apply_guidance(ui, monkeypatch)
    school = SpellFactory.create("Guidance").school
    color = next(
        e["color"]
        for e in active_effects(tiger)
        if e["name"] == "Guidance" and e["tooltip_from"] == SPELL
    )
    from CharacterContent.Spells.SpellFactory import Spell

    assert color == Spell.get_school_color(school)


def test_notes_come_before_the_spell(paladin, monkeypatch):
    ui, _, tiger = paladin
    _apply_guidance(ui, monkeypatch, notes="Stealth")
    _, body = _clicked_popup(ui, monkeypatch, tiger, "Guidance")
    assert body.startswith("<i>Stealth</i>")
    assert "<b>Duration:</b>" in body


def test_a_picked_actions_badge_shows_its_rules_text(fight, monkeypatch):
    ui, _, tiger, _ = fight
    action = EffectOption(
        name="Sticky Web",
        kind=MONSTER_ACTION,
        tooltip="Dexterity Saving Throw: DC 12.\nFailure: the target is webbed.",
    )
    ui._give_effect_condition(
        tiger, CustomEffect("Sticky Web", "Webbed", pick=action), "Webbed"
    )
    heading, body = _clicked_popup(ui, monkeypatch, tiger, "Webbed")
    assert heading == "Webbed"
    assert "<b style='color:#c9a84c; font-size:14px;'>Sticky Web</b>" in body
    assert "DC 12.<br>Failure: the target is webbed." in body


def test_a_picked_features_badge_shows_the_feature(paladin, monkeypatch):
    ui, edmund, tiger = paladin
    feature = edmund["_feature_objects"][0]
    option = EffectOption(name=feature.name, kind=FEATURE)
    ui._give_effect_condition(
        tiger, CustomEffect(feature.name, "Blessed", pick=option), "Blessed"
    )
    _, body = _clicked_popup(ui, monkeypatch, tiger, "Blessed")
    assert body == ui._feature_condition_tooltip(edmund, feature)


def test_an_effect_typed_by_hand_shows_only_its_notes(fight, monkeypatch):
    ui, _, tiger, _ = fight
    ui._give_effect_condition(
        tiger, CustomEffect("Vines", "Tangled", notes="DC 13"), "Tangled"
    )
    _, body = _clicked_popup(ui, monkeypatch, tiger, "Tangled")
    assert body == "DC 13"


def test_a_spells_badge_shows_the_spell_after_a_restart(fight, monkeypatch):
    """A spell's card isn't kept in the log, so a Bless badge restored with
    the fight is read from the spell again."""
    ui, _, tiger, _ = fight
    tiger["conditions"].append("Bless")
    ui._rebuild_card(tiger)
    heading, body = _clicked_popup(ui, monkeypatch, tiger, "Bless")
    assert heading == "Bless" and "<b>Duration:</b>" in body


def test_a_rules_conditions_badge_still_shows_its_rule(fight, monkeypatch):
    ui, _, tiger, _ = fight
    shown = []
    monkeypatch.setattr(ui, "_show_condition_info", shown.append)
    tiger["conditions"].append("Prone")
    ui._rebuild_card(tiger)
    _badge(ui, tiger, "Prone").click()
    assert shown == ["Prone"]


def test_picking_a_monsters_attack(monster, monkeypatch):
    ui, *_ = monster
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Scimitar")
    form = _form(dlg)
    assert form["name"] == "Scimitar"
    assert form["roll"] == ATTACK_ROLL
    assert form["bonus"] == 4
    assert form["damage"] == "1d6 + 2 Slashing"
    assert form["type"] == DamageType.SLASHING.value  # as typing it would set it


def test_picking_a_monsters_save(monster, monkeypatch):
    ui, *_ = monster
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, BREATH["name"])
    form = _form(dlg)
    assert (form["roll"], form["ability"], form["dc"]) == (SAVING_THROW, "DEX", 13)
    assert form["half"]
    assert form["damage"] == "4d6 Fire"


def test_a_monsters_rider_is_in_the_note(monster, monkeypatch):
    ui, *_ = monster
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, REND["name"])
    assert "Also: " in _form(dlg)["note"]
    assert dlg.layout().totalHeightForWidth(dlg.width()) <= 600


def test_picking_a_spell(paladin, monkeypatch):
    ui, edmund, _ = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Hold Person")
    form = _form(dlg)
    assert form["ability"] == "WIS"
    assert form["dc"] == known_save_dc(edmund)
    assert form["condition"] == "Paralyzed"
    assert form["repeat"] and form["concentrates"]
    assert form["duration"] == {"seconds": 60}
    assert form["action"] == "Action"
    assert form["damage"] == ""
    assert "No slot of level 2" in form["note"]  # Edmund has level 1 slots only


def test_picking_a_players_own_spell_spends_a_slot(paladin, monkeypatch):
    ui, *_ = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Bless")
    form = _form(dlg)
    assert form["slot"] == 1
    assert form["condition"] == "Bless"
    assert form["ability"] is None


def test_picking_a_weapon(paladin, monkeypatch):
    ui, edmund, _ = paladin
    sheet = edmund["_stat_block"]
    longsword = next(w for w in edmund["_weapons_objects"] if w.name == "Longsword")
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Longsword")
    form = _form(dlg)
    assert form["roll"] == ATTACK_ROLL
    assert form["bonus"] == longsword.calculate_total_attack_roll_bonus_int(sheet)
    assert form["action"] == "Action"


def test_a_second_pick_replaces_the_first(paladin, monkeypatch):
    ui, edmund, _ = paladin
    edmund["spell_slots"] = {3: 2}
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Fireball")
    assert _form(dlg)["damage"] == "8d6 Fire"
    _pick(dlg, "Hold Person")
    form = _form(dlg)
    assert form["damage"] == ""
    assert form["type"] is None
    assert not form["half"]
    assert form["ability"] == "WIS"
    _pick(dlg, "Bless")
    form = _form(dlg)
    assert form["ability"] is None
    assert not form["repeat"]
    assert form["duration"] == {"seconds": 60}


def test_a_pick_clears_a_type_left_from_before(monster, monkeypatch):
    """The dropdown starting on the source's last type would otherwise
    disagree with the pick's damage."""
    ui, pirate, _ = monster
    pirate["_last_damage_type"] = DamageType.COLD.value
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, BREATH["name"])
    assert _form(dlg)["type"] == FIRE


def test_the_search_filters(paladin, monkeypatch):
    ui, *_ = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _search(dlg).setText("bolt")
    shown = [
        row.data(0, Qt.ItemDataRole.UserRole).name
        for row in _rows(dlg)
        if not row.isHidden()
    ]
    assert "Guiding Bolt" in shown
    assert all("bolt" in name.lower() for name in shown)


def test_enter_picks_the_top_match_then_applies(paladin, monkeypatch):
    answer_out_of_resources(monkeypatch)  # Edmund has no slot for the spell picked.
    ui, _, tiger = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _search(dlg).setText("hold person")
    _search(dlg).returnPressed.emit()
    assert _form(dlg)["name"] == "Hold Person"
    assert ui.history == []
    _d20s(monkeypatch, 1)
    _search(dlg).returnPressed.emit()
    assert "Paralyzed" in tiger["conditions"]
    assert len(ui.history) == 1


def test_enter_with_no_match_does_nothing(paladin, monkeypatch):
    ui, *_ = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _search(dlg).setText("zzzz")
    _search(dlg).returnPressed.emit()
    _search(dlg).returnPressed.emit()
    assert _form(dlg)["name"] == ""
    assert ui.history == []


def test_double_clicking_applies(paladin, monkeypatch):
    answer_out_of_resources(monkeypatch)  # Edmund has no slot for the spell picked.
    ui, _, tiger = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    monkeypatch.setattr(random, "randint", lambda low, high: 1)
    _tree(dlg).itemActivated.emit(_row(dlg, "Fireball"), 0)
    assert tiger["hp"] == tiger["max_hp"] - 8  # failed: every die a 1
    assert "Edmund casts Fireball" in _log(ui)


def test_a_category_row_does_nothing(paladin, monkeypatch):
    ui, *_ = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _tree(dlg).setCurrentItem(_tree(dlg).topLevelItem(0))
    _tree(dlg).itemActivated.emit(_tree(dlg).topLevelItem(0), 0)
    assert _form(dlg)["name"] == ""
    assert ui.history == []


def test_a_higher_slot_upcasts(paladin, monkeypatch):
    ui, edmund, _ = paladin
    edmund["spell_slots"] = {3: 2, 5: 1}
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Fireball")
    slots = _combo(dlg, "spellSlot")
    assert slots.currentData() == 3
    slots.setCurrentIndex(slots.findData(5))
    assert _form(dlg)["damage"] == "10d6 Fire"
    slots.setCurrentIndex(slots.findData(None))
    assert _form(dlg)["damage"] == "8d6 Fire"


def test_a_hand_edit_survives_a_slot_change(paladin, monkeypatch):
    ui, edmund, _ = paladin
    edmund["spell_slots"] = {3: 2, 5: 1}
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Fireball")
    dlg.findChild(QLineEdit, "effectDamage").setText("30 fire")
    slots = _combo(dlg, "spellSlot")
    slots.setCurrentIndex(slots.findData(5))
    assert _form(dlg)["damage"] == "30 fire"


def test_every_field_stays_editable_after_a_pick(paladin, monkeypatch):
    answer_out_of_resources(monkeypatch)  # Edmund has no level 2 slot for Hold Person.
    ui, _, tiger = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Hold Person")
    _combo(dlg, "conditionName").setCurrentText("Stunned")
    dlg.findChild(QSpinBox, "saveDc").setValue(30)
    _d20s(monkeypatch, 15)
    _apply(dlg)
    assert "Stunned" in tiger["conditions"]
    assert "Paralyzed" not in tiger["conditions"]


def test_a_greyed_action_can_be_picked_and_asks_first(monster, monkeypatch):
    ui, pirate, tiger = monster
    name = BREATH["name"]
    pirate["spent_abilities"] = {name: 1}
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    row = _row(dlg, name)
    assert not row.isDisabled()
    assert "(spent)" in row.text(0)
    _pick(dlg, name)
    assert _form(dlg)["name"] == name
    asked = answer_out_of_resources(monkeypatch, yes=False)
    _apply(dlg)
    assert asked == [f"Pirate is out of:\n\n•  {name}: spent\n\nUse {name} anyway?"]
    assert pirate["spent_abilities"] == {name: 1}
    assert tiger["hp"] == tiger["max_hp"]
    assert ui.history == []
    # Yes uses it all the same.
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, name)
    answer_out_of_resources(monkeypatch, yes=True)
    monkeypatch.setattr(random, "randint", lambda low, high: 1)
    _apply(dlg)
    assert pirate["spent_abilities"] == {name: 2}
    assert tiger["hp"] < tiger["max_hp"]


def test_one_question_lists_everything_the_source_is_out_of(paladin, monkeypatch):
    ui, edmund, tiger = paladin
    edmund["action_uses"] = {"Action": 1}
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Hold Person")
    asked = answer_out_of_resources(monkeypatch, yes=False)
    _apply(dlg)
    assert asked == [
        "Edmund is out of:\n\n"
        "•  Spell slots: none of level 2 or higher left\n"
        "•  Action: already used this turn\n\n"
        "Use Hold Person anyway?"
    ]
    assert "Hold Person" not in tiger["conditions"]
    assert edmund["action_uses"] == {"Action": 1}
    assert ui.history == []


def test_a_feature_with_no_uses_left_asks_first(paladin, monkeypatch):
    ui, edmund, _ = paladin
    edmund["feature_uses_used"] = {"Channel Divinity": 99}
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Divine Sense")
    asked = answer_out_of_resources(monkeypatch, yes=True)
    _apply(dlg)
    assert "Channel Divinity: no uses left" in asked[0]
    assert edmund["feature_uses_used"] == {"Channel Divinity": 100}


def test_a_hand_typed_effect_still_spends_nothing_else(monster, monkeypatch):
    ui, pirate, tiger = monster
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    dlg.findChild(QLineEdit, "effectDamage").setText("6 fire")
    _apply(dlg)
    assert tiger["hp"] == tiger["max_hp"] - 6
    assert "spent_abilities" not in pirate
    assert "uses" not in _log(ui)


# Spending


def test_a_picked_spell_is_cast_and_undoes_in_one(paladin, monkeypatch):
    ui, edmund, tiger = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Bless")
    _apply(dlg)
    assert edmund["spell_slots"] == {1: 2}
    assert edmund["stats"]["spells_cast"] == 1
    assert edmund["stats"]["spells_cast_by_name"] == {"Bless": 1}
    assert edmund["action_uses"] == {"Action": 1}
    assert "Bless" in tiger["conditions"]
    assert "Edmund casts Bless" in _log(ui)
    ui._undo_last()
    assert edmund["spell_slots"] == {1: 3}
    assert not edmund.get("stats", {}).get("spells_cast")
    assert "Bless" not in tiger["conditions"]
    assert ui.history == []


def test_an_upcast_says_its_level(paladin, monkeypatch):
    ui, edmund, _ = paladin
    edmund["spell_slots"] = {3: 2, 5: 1}
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Fireball")
    slots = _combo(dlg, "spellSlot")
    slots.setCurrentIndex(slots.findData(5))
    monkeypatch.setattr(random, "randint", lambda low, high: 20)
    _apply(dlg)
    assert edmund["spell_slots"] == {3: 2, 5: 0}
    assert "Edmund casts Fireball at level 5" in _log(ui)


def test_a_picked_feature_is_used_with_nothing_else(paladin, monkeypatch):
    ui, edmund, _ = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Divine Sense")
    _apply(dlg)
    assert edmund["feature_uses_used"] == {"Channel Divinity": 1}
    assert edmund["stats"]["features_enabled_by_name"] == {"Channel Divinity": 1}
    assert "Edmund uses Channel Divinity" in _log(ui)
    ui._undo_last()
    assert not edmund.get("feature_uses_used")
    assert ui.history == []


def test_a_pick_without_a_source_spends_nothing(paladin, monkeypatch):
    ui, edmund, tiger = paladin
    ui.selected_character = None
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Bless")
    _apply(dlg)
    assert "Bless" in tiger["conditions"]
    assert edmund["spell_slots"] == {1: 3}
    assert "casts" not in _log(ui)


def test_a_spell_attack_is_one_line_the_player_link_reads(paladin, monkeypatch):
    ui, _, tiger = paladin
    tiger["ac"] = 10
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Chill Touch")
    monkeypatch.setattr(random, "randint", lambda low, high: 10)
    _apply(dlg)
    texts = [event["text"] for event in ui._read_log()["round_1"]]
    # One line for the cast, none more for the attack; its badge is its own.
    assert [text for text in texts if "Chill Touch" in text] == [
        "[Edmund's turn] Edmund casts Chill Touch",
        "[Edmund's turn] Tiger gains Chill Touch from Edmund",
    ]
    (round_log,) = ui._public_log()
    lines = [line for turn in round_log["turns"] for line in turn["lines"]]
    assert lines[0]["text"] == "Edmund casts Chill Touch"
    hit = next(line for line in lines if line["kind"] == "hit")
    assert hit["amount"] == f"10 {DamageType.NECROTIC.value}"


def test_a_recharge_is_spent_and_shows_in_the_turn_column(monster, monkeypatch):
    ui, pirate, tiger = monster
    QApplication.processEvents()
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, BREATH["name"])
    monkeypatch.setattr(random, "randint", lambda low, high: 1)
    _apply(dlg)
    assert pirate["spent_abilities"] == {BREATH["name"]: 1}
    assert tiger["hp"] < tiger["max_hp"]
    buttons = [
        b.text() for b in ui._actions_box.findChildren(QPushButton) if not b.isHidden()
    ]
    assert any(f"{BREATH['name']} (spent)" in text for text in buttons), buttons
    assert _log(ui).count(f"Pirate uses {BREATH['name']}") == 1
    ui._undo_last()
    assert not pirate.get("spent_abilities")
    assert tiger["hp"] == tiger["max_hp"]


def test_a_limited_attack_is_logged_once(monster, monkeypatch):
    ui, *_ = monster
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, REND["name"])
    monkeypatch.setattr(random, "randint", lambda low, high: 15)
    _apply(dlg)
    assert _log(ui).count(f"uses {REND['name']}") == 1


def test_a_legendary_action_is_spent(monster, monkeypatch):
    ui, pirate, tiger = monster
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, GAZE["name"])
    form = _form(dlg)
    assert (form["ability"], form["dc"], form["condition"]) == ("WIS", 14, "Frightened")
    _d20s(monkeypatch, 1)
    _apply(dlg)
    assert pirate["legendary_actions_left"] == 1
    assert "Frightened" in tiger["conditions"]
    ui._undo_last()
    assert "legendary_actions_left" not in pirate


def test_a_legendary_action_costing_more_than_is_left_is_greyed(monster, monkeypatch):
    ui, pirate, _ = monster
    pirate["legendary_actions_left"] = 1
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    row = _row(dlg, GAZE["name"])
    assert "(1 left)" in row.text(0)
    assert row.foreground(0).color().name() == "#6a6a7a"
    assert not row.isDisabled()  # still the GM's to pick: applying it asks


def test_without_a_source_a_monster_spends_nothing(monster, monkeypatch):
    ui, pirate, _ = monster
    ui.selected_character = None
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, BREATH["name"])
    monkeypatch.setattr(random, "randint", lambda low, high: 1)
    _apply(dlg)
    assert "spent_abilities" not in pirate


def test_a_picked_spell_is_logged_for_the_party_replay(paladin, monkeypatch):
    """The party's state is replayed from these events (logging_mixin), as a
    Cast Spell's are."""
    ui, *_ = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Bless")
    _apply(dlg)
    events = [e for e in ui._read_log()["round_1"] if e.get("character") == "Edmund"]
    actions = [(e.get("action"), e.get("value")) for e in events if e.get("action")]
    assert (Action.CAST_SPELL, {"spell_name": "Bless"}) in actions
    assert (Action.REMOVE_SPELL_SLOT, 1) in actions


def test_a_spent_recharge_survives_reloading_the_fight(monster, tmp_path, monkeypatch):
    ui, *_ = monster
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, BREATH["name"])
    monkeypatch.setattr(random, "randint", lambda low, high: 1)
    _apply(dlg)
    fresh = make_ui(tmp_path, [])
    fresh._load_log_from_path(str(ui.log_file))
    pirate = next(c for c in fresh.characters if c["name"] == "Pirate")
    assert pirate["spent_abilities"] == {BREATH["name"]: 1}


# What review found


PARALYZING_TOUCH = {
    "name": "Paralyzing Touch",
    "description": "Melee Attack Roll: +12, reach 5 ft. Hit: 15 (3d6 + 5) Cold damage,"
    " and the target has the Paralyzed condition until the start of the lich's next"
    " turn.",
}


def test_retyping_the_name_drops_the_pick(paladin, monkeypatch):
    """The GM picked Divine Sense, then typed in something else: that's
    their own effect, so Channel Divinity isn't used."""
    ui, edmund, tiger = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Divine Sense")
    name = dlg.findChild(QLineEdit, "effectName")
    name.setText("Poison Spray")
    name.textEdited.emit("Poison Spray")
    assert _form(dlg)["note"] == ""
    assert not _tree(dlg).selectedItems()
    _combo(dlg, "conditionName").setCurrentText("Poisoned")
    _apply(dlg)
    assert "Poisoned" in tiger["conditions"]
    assert not edmund.get("feature_uses_used")
    assert "Channel Divinity" not in _log(ui)


def test_a_pick_filling_the_name_keeps_it(paladin, monkeypatch):
    ui, edmund, _ = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Divine Sense")
    dlg.findChild(QLineEdit, "effectName").textEdited.emit("Divine Sense")
    _apply(dlg)
    assert edmund["feature_uses_used"] == {"Channel Divinity": 1}


def test_a_passive_feature_cant_be_applied_by_itself(paladin, monkeypatch):
    ui, edmund, _ = paladin
    # One always on and not described: no uses, no action, nothing to apply
    # (Edmund's own such features all say they have nothing to apply).
    edmund["_feature_objects"] = [
        *edmund["_feature_objects"],
        Feature(name="Plain Feature", origin="Test"),
    ]
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    options = [row.data(0, Qt.ItemDataRole.UserRole) for row in _rows(dlg)]
    passive = next(o for o in options if o.kind == "feature" and not o.is_tracked)
    assert passive.name == "Plain Feature"
    _pick(dlg, passive.name)
    _apply(dlg)
    assert ui.history == []
    labels = [label.text() for label in dlg.findChildren(QLabel)]
    assert any("Add a saving throw" in text for text in labels)


def test_a_second_weapon_attack_costs_no_action(paladin, monkeypatch):
    ui, edmund, _ = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Longsword")
    assert _form(dlg)["action"] == "Action"
    edmund["action_uses"] = {"Action": 1}
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Longsword")
    assert _form(dlg)["action"] is None


def test_a_condition_till_a_turn_gets_that_duration(monster, monkeypatch):
    ui, pirate, _ = monster
    pirate["actions"] = [PARALYZING_TOUCH]
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Paralyzing Touch: Paralyzed")  # its hit's rider row (6.4)
    form = _form(dlg)
    assert form["condition"] == "Paralyzed"
    assert form["duration"] == {"until": "start", "of": "source"}


def test_a_spells_turn_long_condition_gets_that_duration(paladin, monkeypatch):
    ui, *_ = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Sleep")  # "until the end of its next turn"
    assert _form(dlg)["duration"] == {"until": "end", "of": "target"}


def test_enter_after_a_new_search_picks_again(paladin, monkeypatch):
    answer_out_of_resources(monkeypatch)  # Edmund has no slot for the spell picked.
    """Fire Bolt picked, then "fireball" typed: Enter picks Fireball, it
    doesn't cast Fire Bolt."""
    ui, *_ = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _pick(dlg, "Fire Bolt")
    _search(dlg).setText("fireball")
    _search(dlg).returnPressed.emit()
    assert _form(dlg)["name"] == "Fireball"
    assert ui.history == []
    monkeypatch.setattr(random, "randint", lambda low, high: 1)
    _search(dlg).returnPressed.emit()
    assert "Edmund casts Fireball" in _log(ui)
    assert "Fire Bolt" not in _log(ui)


def test_enter_on_a_new_search_with_the_same_top_match_picks_it_again(
    paladin, monkeypatch
):
    ui, *_ = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _search(dlg).setText("fireb")
    _search(dlg).returnPressed.emit()
    dlg.findChild(QLineEdit, "effectDamage").setText("1 fire")
    _search(dlg).setText("firebal")
    _search(dlg).returnPressed.emit()
    assert _form(dlg)["damage"] == "8d6 Fire"  # picked again
    assert ui.history == []


# A save total rolled at the table, for any target


def _save_dialog(ui, monkeypatch, dc: int = 15):
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    combo = _combo(dlg, "saveAbility")
    combo.setCurrentIndex(combo.findData("DEX"))
    dlg.findChild(QSpinBox, "saveDc").setValue(dc)
    dlg.findChild(QLineEdit, "effectDamage").setText("20 fire")
    return dlg


def test_every_target_has_a_save_total(fight, monkeypatch):
    ui, *_ = fight
    dlg = _save_dialog(ui, monkeypatch)
    boxes = dlg.findChildren(QLineEdit, "typedTotal")
    assert sorted(box.accessibleName() for box in boxes) == ["Bandit (Pirate)", "Tiger"]
    assert all(box.isVisibleTo(dlg) and box.isEnabled() for box in boxes)
    assert boxes[0].placeholderText() == "Total, or blank to roll"
    assert "save bonus" in boxes[0].toolTip()


def test_a_monsters_typed_total_is_used(fight, monkeypatch):
    ui, _, tiger, bandit = fight
    dlg = _save_dialog(ui, monkeypatch)
    _typed_total(dlg, "Tiger").setText("20")
    _d20s(monkeypatch, 1)  # only the Bandit's die is rolled
    _apply(dlg)
    assert tiger["hp"] == tiger["max_hp"] - 10  # saved: half
    assert bandit["hp"] == bandit["max_hp"] - 20
    assert "rolled 20" in _log(ui)


def test_a_typed_sum(fight, monkeypatch):
    ui, _, tiger, _ = fight
    dlg = _save_dialog(ui, monkeypatch)
    _typed_total(dlg, "Tiger").setText("9+5")
    _d20s(monkeypatch, 1)
    _apply(dlg)
    assert "rolled 14" in _log(ui)
    assert tiger["hp"] == tiger["max_hp"] - 20  # 14 misses DC 15


def test_a_natural_roll_isnt_a_save_total(fight, monkeypatch):
    ui, _, tiger, _ = fight
    dlg = _save_dialog(ui, monkeypatch)
    _typed_total(dlg, "Tiger").setText("nat 20")
    _apply(dlg)
    assert ui.history == []
    assert tiger["hp"] == tiger["max_hp"]
    labels = [label.text() for label in dlg.findChildren(QLabel)]
    assert any("Type the total" in text for text in labels), labels


def test_a_typed_failure_can_spend_legendary_resistance(fight, monkeypatch):
    ui, _, tiger, _ = fight
    tiger["legendary_resistances"] = 2
    dlg = _save_dialog(ui, monkeypatch)
    dlg.findChild(QCheckBox, "useLegendaryResistance").setChecked(True)
    _typed_total(dlg, "Tiger").setText("3")
    _d20s(monkeypatch, 20)
    _apply(dlg)
    assert tiger["legendary_resistances_left"] == 1
    assert tiger["hp"] == tiger["max_hp"] - 10
    assert "rolled 3" in _log(ui)


def test_an_automatic_failure_beats_a_typed_total_in_the_dialog(fight, monkeypatch):
    ui, _, tiger, _ = fight
    tiger["conditions"].append("Stunned")
    dlg = _save_dialog(ui, monkeypatch)
    _typed_total(dlg, "Tiger").setText("30")
    _d20s(monkeypatch, 1)
    _apply(dlg)
    assert tiger["hp"] == tiger["max_hp"] - 20


def test_the_dialog_fits_with_eight_targets(tmp_path, monkeypatch):
    ui = make_ui(tmp_path, [_named(Pirate(), f"Pirate {i}") for i in range(9)])
    for i, char in enumerate(ui.characters):
        ui._initiative_inputs[id(char)].setText(str(20 - i))
    ui._start_combat()
    for i, char in enumerate(ui.characters[1:]):
        ui._select_target_character(char, ctrl=i > 0)
    assert len(ui.target_characters) == 8
    dlg = _save_dialog(ui, monkeypatch)
    assert len(dlg.findChildren(QLineEdit, "typedTotal")) == 8
    assert dlg.layout().totalHeightForWidth(dlg.width()) <= 600
    _combo(dlg, "rollKind").setCurrentText(ATTACK_ROLL)
    assert dlg.layout().totalHeightForWidth(dlg.width()) <= 600


# ---------------------------------------------------------------------------
# A feature described by its own combat_effects() (Model/Content/CombatEffect.py)
# fills the form, and Apply spends it as Enable Feature would


def _party_fight(tmp_path, builder):
    """The player built by `builder`, the source, targeting a Tiger."""
    ui = make_ui(tmp_path, [Tiger()], [builder().build()])
    player, tiger = ui.characters
    ui._initiative_inputs[id(player)].setText("15")
    ui._initiative_inputs[id(tiger)].setText("10")
    ui._start_combat()
    ui._select_character(player)
    ui._select_target_character(tiger)
    return ui, player, tiger


def _pick_and_apply(ui, monkeypatch, search: str) -> dict:
    """Search for it, pick it, check where its numbers came from, and apply."""
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _search(dlg).setText(search)
    _search(dlg).returnPressed.emit()
    details = dlg.findChild(QTextBrowser, "effectDetails").toPlainText()
    assert "filled in from the feature's combat data" in details
    form = _form(dlg)
    _apply(dlg)
    return form


def test_jolt_to_life_rolls_its_save_and_spends_its_feature(tmp_path, monkeypatch):
    from Builds.Characters.Y2024_Artificer_Reanimator_Dessie import (
        Y2024ArtificerReanimatorDessieCharacterBuilder as Dessie,
    )

    ui, dessie, tiger = _party_fight(tmp_path, Dessie)
    form = _pick_and_apply(ui, monkeypatch, "jolt")
    assert (form["ability"], form["damage"], form["half"]) == (
        "DEX",
        "2d4 Lightning",
        True,
    )
    assert dessie["feature_uses_used"] == {"Reanimator's Skill Set": 1}
    assert dessie["action_uses"]["Action"] == 1
    log = _log(ui)
    assert "Dessie uses Reanimator's Skill Set" in log
    assert "Dexterity save against Jolt to Life" in log


def test_bardic_inspiration_puts_its_badge_on_the_target(tmp_path, monkeypatch):
    from Builds.Characters.Y2024_Bard_Valor_Thomas import (
        Y2024BardValorThomasCharacterBuilder as Thomas,
    )

    ui, thomas, tiger = _party_fight(tmp_path, Thomas)
    _pick_and_apply(ui, monkeypatch, "bardic")
    assert "Bardic Inspiration" in tiger["conditions"]
    (timer,) = timers(tiger)
    assert timer["time_left"] == 60 * 60  # once within the next hour
    assert thomas["feature_uses_used"] == {"Bardic Inspiration": 1}
    assert thomas["action_uses"]["Bonus Action"] == 1
    heading, body = _clicked_popup(ui, monkeypatch, tiger, "Bardic Inspiration")
    assert heading == "Bardic Inspiration"
    assert "Bard Level 1" in body  # the feature's card


def test_favored_enemys_hunters_mark_is_the_spells_badge(tmp_path, monkeypatch):
    from Builds.Characters.Y2024_Ranger_Drakewarden_Hanna import (
        Y2024RangerDrakewardenHannaCharacterBuilder as Hanna,
    )

    ui, hanna, tiger = _party_fight(tmp_path, Hanna)
    slots = dict(hanna["spell_slots"])
    _pick_and_apply(ui, monkeypatch, "favored")
    assert "Hunter's Mark" in tiger["conditions"]
    assert "Concentrating" in hanna["conditions"]
    assert hanna["spell_slots"] == slots  # cast without a slot
    assert hanna["feature_uses_used"] == {"Favored Enemy": 1}
    _, body = _clicked_popup(ui, monkeypatch, tiger, "Hunter's Mark")
    assert "<b>Duration:</b> Concentration, up to 1 hour" in body  # the spell's card


# ---------------------------------------------------------------------------
# Healing and Temporary Hit Points: the amount box's other kinds, which every
# target gets, whatever the roll


def _amount_kind(dlg, kind: str):
    _chips(dlg, "amountKindButtons")[kind].click()


def _hurt(char: dict, by: int):
    char["hp"] = char["max_hp"] - by


def test_healing_heals_every_target(fight, monkeypatch):
    ui, pirate, tiger, bandit = fight
    _hurt(tiger, 10)
    _hurt(bandit, 3)
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _amount_kind(dlg, HEALING)
    dlg.findChild(QLineEdit, "effectDamage").setText("5")
    _apply(dlg)
    assert tiger["hp"] == tiger["max_hp"] - 5
    assert bandit["hp"] == bandit["max_hp"]  # no more than its maximum
    assert "Tiger heals 5 HP" in _log(ui)
    assert "heals 5" in ui._action_result_label.text()
    assert len(ui.history) == 1  # one undo


def test_healing_dice_are_rolled_once_for_everyone(fight, monkeypatch):
    ui, _, tiger, bandit = fight
    _hurt(tiger, 20)
    _hurt(bandit, 20)
    rolls = iter([3, 5])
    monkeypatch.setattr(random, "randint", lambda low, high: next(rolls))
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _amount_kind(dlg, HEALING)
    dlg.findChild(QLineEdit, "effectDamage").setText("2d8 + 3")
    _apply(dlg)
    assert tiger["hp"] == bandit["hp"] - bandit["max_hp"] + tiger["max_hp"]
    assert tiger["max_hp"] - tiger["hp"] == 20 - (3 + 5 + 3)


def test_healing_brings_a_player_at_0_hit_points_to(paladin_fight, monkeypatch):
    """Regaining any Hit Points ends the Unconscious from 0 Hit Points."""
    ui, edmund, _ = paladin_fight
    edmund["hp"] = 0
    edmund["conditions"].append("Unconscious")
    edmund["death_saves_fail"] = 1
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _amount_kind(dlg, HEALING)
    dlg.findChild(QLineEdit, "effectDamage").setText("4")
    _apply(dlg)
    assert edmund["hp"] == 4
    assert "Unconscious" not in edmund["conditions"]
    assert edmund["death_saves_fail"] == 0
    assert "Edmund regains consciousness with 4 HP" in _log(ui)


def test_healing_goes_to_every_target_whatever_the_save(fight, monkeypatch):
    """The save still decides the condition: those who save don't get it."""
    ui, _, tiger, bandit = fight
    _hurt(tiger, 10)
    _hurt(bandit, 10)
    _d20s(monkeypatch, 20, 1)  # the Tiger saves, the Bandit doesn't
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _chips(dlg, "saveAbilityButtons")["DEX"].click()
    dlg.findChild(QSpinBox, "saveDc").setValue(15)
    _amount_kind(dlg, HEALING)
    dlg.findChild(QLineEdit, "effectDamage").setText("6")
    _combo(dlg, "conditionName").setCurrentText("Prone")
    _apply(dlg)
    assert tiger["hp"] == bandit["hp"] - bandit["max_hp"] + tiger["max_hp"]
    assert tiger["max_hp"] - tiger["hp"] == 4  # both healed 6
    assert "Prone" not in tiger["conditions"]
    assert "Prone" in bandit["conditions"]


def test_temporary_hit_points_for_every_target(fight, monkeypatch):
    ui, _, tiger, bandit = fight
    bandit["temp_hp"] = 9  # they don't stack: the higher stays
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _amount_kind(dlg, TEMP_HP)
    dlg.findChild(QLineEdit, "effectDamage").setText("7")
    _apply(dlg)
    assert tiger["temp_hp"] == 7
    assert bandit["temp_hp"] == 9
    assert tiger["hp"] == tiger["max_hp"]  # no damage
    assert "7 temp HP" in ui._action_result_label.text()


def test_healing_has_no_damage_type(fight, monkeypatch):
    ui, _, tiger, _ = fight
    _hurt(tiger, 10)
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _amount_kind(dlg, HEALING)
    dlg.findChild(QLineEdit, "effectDamage").setText("5 fire")
    _apply(dlg)
    assert tiger["hp"] == tiger["max_hp"] - 10
    assert ui.history == []
    labels = [label.text() for label in dlg.findChildren(QLabel)]
    assert any("Healing has no damage type" in text for text in labels), labels


def test_healing_alone_is_enough_to_apply(fight, monkeypatch):
    ui, _, tiger, _ = fight
    _hurt(tiger, 2)
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _choose_roll(dlg, "No roll")
    _amount_kind(dlg, HEALING)
    dlg.findChild(QLineEdit, "effectDamage").setText("2")
    _apply(dlg)
    assert tiger["hp"] == tiger["max_hp"]


def test_the_damage_only_controls_go_away_for_healing(fight, monkeypatch):
    ui, *_ = fight
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _choose_roll(dlg, SAVING_THROW)
    damage_only = [
        _combo(dlg, "damageType"),
        dlg.findChild(QCheckBox, "countResistances"),
        dlg.findChild(QCheckBox, "halfOnSave"),
    ]
    assert all(widget.isVisibleTo(dlg) for widget in damage_only)
    for kind in (HEALING, TEMP_HP):
        _amount_kind(dlg, kind)
        assert not any(widget.isVisibleTo(dlg) for widget in damage_only), kind
    _amount_kind(dlg, DAMAGE_AMOUNT)
    assert all(widget.isVisibleTo(dlg) for widget in damage_only)
    labels = [label.text() for label in dlg.findChildren(QLabel)]
    assert "Damage" in labels


def test_the_preview_of_healing(fight, monkeypatch):
    ui, *_ = fight
    monkeypatch.setattr(random, "randint", lambda *a: pytest.fail("rolled"))
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _choose_roll(dlg, "No roll")
    _amount_kind(dlg, HEALING)
    dlg.findChild(QLineEdit, "effectDamage").setText("2d8 + 3")
    preview = dlg.findChild(QLabel, "effectPreview").text()
    assert preview == "On 2 targets: heals 2d8 + 3 for all"


def test_picking_cure_wounds_fills_in_healing(paladin, monkeypatch):
    """2d8 plus Edmund's spellcasting ability modifier, his Charisma."""
    ui, edmund, tiger = paladin
    _hurt(tiger, 20)
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _search(dlg).setText("cure wounds")
    _search(dlg).returnPressed.emit()
    modifier = edmund["_stat_block"].get_charisma_modifier()
    assert _combo(dlg, "amountKind").currentText() == HEALING
    assert _form(dlg)["damage"] == f"2d8 + {modifier}"
    assert not _combo(dlg, "damageType").isVisibleTo(dlg)
    _apply(dlg)
    assert tiger["hp"] > tiger["max_hp"] - 20
    assert "Edmund casts Cure Wounds" in _log(ui)


def test_picking_a_damage_spell_after_healing_is_damage_again(paladin, monkeypatch):
    ui, *_ = paladin
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _search(dlg).setText("cure wounds")
    _search(dlg).returnPressed.emit()
    _search(dlg).setText("fireball")
    _search(dlg).returnPressed.emit()
    assert _combo(dlg, "amountKind").currentText() == DAMAGE_AMOUNT
    assert _form(dlg)["damage"] == "8d6 Fire"
