"""The Custom dialog as a save-or-suffer effect (saves.py,
ConditionsMixin._apply_custom_effect): a saving throw rolled for every target, or
an attack roll against each one's AC, damage rolled once for all of them, and a
condition on those who failed or were hit, all one undo. Expected values come
from the rules: Saving-Throw, Critical-Hit and the Paralyzed, Petrified, Stunned,
Unconscious and Restrained glossary entries."""

import random

import pytest
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
)

from Builds.Characters.Y2024_Paladin_Devotion_Edmund import (
    Y2024PaladinDevotionEdmundCharacterBuilder as Edmund,
)
from CharacterContent.Spells.SpellFactory import SpellFactory
from Combat.Combatants import Pirate, Tiger
from Combat.CombatUIQt.amounts import AmountError
from Combat.CombatUIQt.attack_rolls import AttackRoll
from Combat.CombatUIQt.saves import (
    ATTACK_ROLL,
    CustomEffect,
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
from Model.Creatures.Combatants import DamageTypeEntry
from tests._combat_ui import make_ui, open_dialog

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
    assert bandit["custom_condition_descriptions"] == {"Prone": "Knocked flat"}


def test_a_condition_has_its_duration(fight, monkeypatch):
    ui, _, _, bandit = fight
    _d20s(monkeypatch, 1, 1)
    ui._apply_custom_effect(
        CustomEffect(condition="Hexed", ability="DEX", dc=15, duration={"seconds": 60})
    )
    assert bandit["timed_conditions"][0]["time_left"] == 60


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
    box = dlg.findChild(QCheckBox, "useLegendaryResistance")
    assert not box.isVisibleTo(dlg)
    tiger["legendary_resistances"] = 3
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
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


def test_a_players_total_is_typed_in_the_dialog(paladin_fight, monkeypatch):
    ui, edmund, tiger = paladin_fight
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    combo = _combo(dlg, "saveAbility")
    combo.setCurrentIndex(combo.findData("WIS"))
    dlg.findChild(QSpinBox, "saveDc").setValue(15)
    dlg.findChild(QLineEdit, "effectDamage").setText("20 fire")
    (total,) = dlg.findChildren(QLineEdit, "typedTotal")
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
    (total,) = dlg.findChildren(QLineEdit, "typedTotal")
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
    (total,) = dlg.findChildren(QLineEdit, "typedTotal")
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
    assert "repeat_saves" not in tiger
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
    assert tiger["repeat_saves"]
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
    assert "repeat_saves" not in tiger


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
    assert tiger["repeat_saves"][0]["dc"] == 15
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
    assert loaded["timed_conditions"][0]["name"] == "Slowed"
    assert loaded["custom_condition_descriptions"] == {"Slowed": "Half speed"}


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
    assert "repeat_saves" not in tiger


def test_a_condition_given_twice_repeats_once(fight, monkeypatch):
    ui, _, tiger, _ = fight
    _d20s(monkeypatch, 1, 1, 1, 1)
    ui._apply_custom_effect(_hold())
    ui._apply_custom_effect(_hold())
    assert len(tiger["repeat_saves"]) == 1


def test_a_condition_removed_takes_its_repeat_save_with_it(fight, monkeypatch):
    ui, _, tiger, _ = fight
    _d20s(monkeypatch, 1, 1)
    ui._apply_custom_effect(_hold())
    ui._remove_condition_from(tiger, "Paralyzed")
    assert "repeat_saves" not in tiger


def test_a_repeat_keeps_the_rolls_mode(fight, monkeypatch):
    ui, _, tiger, _ = fight
    tiger["Saving Throws"] = {"WIS": 0}
    _d20s(monkeypatch, 1, 1)
    ui._apply_custom_effect(_hold(mode="Advantage"))
    assert tiger["repeat_saves"][0]["mode"] == "Advantage"
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
    tiger["repeat_saves"][0]["use_legendary_resistance"] = True
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
    dc = dlg.findChild(QSpinBox, "saveDc")
    bonus = dlg.findChild(QSpinBox, "attackBonus")
    ability = _combo(dlg, "saveAbility")

    def labels() -> list[str]:
        return [label.text() for label in dlg.findChildren(type(ui.selected_label))]

    assert dc.isVisibleTo(dlg) and ability.isVisibleTo(dlg)
    assert not bonus.isVisibleTo(dlg)
    assert "Condition (on a failed save)" in labels()

    _combo(dlg, "rollKind").setCurrentText(ATTACK_ROLL)
    assert bonus.isVisibleTo(dlg)
    assert not dc.isVisibleTo(dlg) and not ability.isVisibleTo(dlg)
    assert _combo(dlg, "saveMode").isEnabled()
    assert "Condition (on a hit)" in labels()


def test_the_save_only_ticks_go_away_for_an_attack(fight, monkeypatch):
    ui, _, tiger, _ = fight
    tiger["legendary_resistances"] = 3
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    boxes = [
        dlg.findChild(QCheckBox, name)
        for name in ("halfOnSave", "repeatSave", "useLegendaryResistance")
    ]
    assert all(box.isVisibleTo(dlg) for box in boxes)
    _combo(dlg, "rollKind").setCurrentText(ATTACK_ROLL)
    assert not any(box.isVisibleTo(dlg) for box in boxes)
    _combo(dlg, "rollKind").setCurrentText("Saving throw")
    assert all(box.isVisibleTo(dlg) for box in boxes)


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
    assert "repeat_saves" not in tiger


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
