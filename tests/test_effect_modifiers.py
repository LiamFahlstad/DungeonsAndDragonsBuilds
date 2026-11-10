"""Lasting effects that carry their own modifiers, and the simulator counting
them (plan step 3.3): Bless's 1d4 on attack rolls and saving throws, Shield of
Faith's +2 AC, cover's bonus to Dexterity saves, AttacksAgainst and
Resistance from an effect. Expected values come from the 2024 rules: Bless
("the target adds 1d4 to the attack roll or save"), Shield of Faith ("a +2
bonus to AC for the duration") and the Rules Glossary's Cover ("Half Cover
(+2 bonus to AC and Dexterity saving throws), Three-Quarters Cover (+5 bonus
to AC and Dexterity saving throws) ... a target benefits only from the most
protective degree")."""

import json
import random

import pytest
from PyQt6.QtWidgets import QDialog, QLabel, QMessageBox, QPushButton, QWidget

from CharacterContent.Spells.SpellFactory import SpellFactory
from Combat.Combatants import Pirate, Tiger
from Combat.Effects.active_effects import (
    KEY,
    badge_modifiers,
    ending_conditions,
    find_effect,
    give_modifiers,
    new_effect,
    remove_effect,
    says_something,
    upgrade_old_keys,
)
from Combat.Effects.modifiers import (
    armor_class_bonus,
    attack_plan,
    modifiers_on,
    resists,
    save_plan,
)
from Combat.CombatUIQt.saves import (
    ATTACK_ROLL,
    SPELL,
    CustomEffect,
    EffectOption,
    roll_save,
)
from Core.Definitions import Ability, Condition, DamageType
from Model.Content.CombatEffect import CombatCondition, CombatEffect
from Model.Content.CombatModifiers import (
    ArmorClass,
    AttacksAgainst,
    AutoFail,
    ConditionImmunity,
    CriticalHitsAgainst,
    D20Bonus,
    D20Mode,
    D20Test,
    HasConditions,
    Note,
    Resistance,
    RollMode,
    modifier_from_dict,
    modifier_to_dict,
)
from Model.Creatures.Combatants import Visibility
from tests._combat_ui import make_ui, open_dialog

NEUTRAL = "Neutral"
BLESS = D20Bonus((D20Test.ATTACK_ROLL, D20Test.SAVING_THROW), "1d4")
HALF, THREE_QUARTERS = (
    Visibility.HALF_COVER.value,
    Visibility.THREE_QUARTERS_COVER.value,
)


def _with(*conditions: str, name: str = "Tiger", **keys) -> dict:
    return {"name": name, "conditions": list(conditions), **keys}


def _blessed(name: str = "Tiger", **keys) -> dict:
    char = _with("Bless", name=name, **keys)
    give_modifiers(char, "Bless", (BLESS,))
    return char


def _modifiers(char: dict, name: str) -> list[dict] | None:
    effect = find_effect(char, name)
    return None if effect is None else effect["modifiers"]


def _dice(monkeypatch, d20s=(), d4s=()):
    """random.randint gives these: each d20 of a roll (two a roll), then
    each d4 (Bless's)."""
    d20, d4 = iter(d20s), iter(d4s)
    monkeypatch.setattr(
        random, "randint", lambda low, high: next(d20) if high == 20 else next(d4)
    )


# ---------------------------------------------------------------------------
# A modifier as plain data


@pytest.mark.parametrize(
    "modifier",
    [
        BLESS,
        D20Bonus((D20Test.SAVING_THROW,), "-2", (Ability.DEXTERITY,), True, "x"),
        D20Mode((D20Test.SAVING_THROW,), RollMode.DISADVANTAGE, (Ability.DEXTERITY,)),
        AttacksAgainst(RollMode.ADVANTAGE, "the attacker is within 5 feet"),
        AutoFail((D20Test.SAVING_THROW,), (Ability.STRENGTH, Ability.DEXTERITY)),
        CriticalHitsAgainst(),
        ArmorClass(2),
        Resistance((DamageType.FIRE, DamageType.COLD)),
        Resistance(),
        ConditionImmunity((Condition.POISONED,)),
        HasConditions((Condition.PRONE,)),
        Note("Speed 0"),
    ],
)
def test_a_modifier_reads_back_as_it_was_written(modifier):
    data = modifier_to_dict(modifier)
    assert json.loads(json.dumps(data)) == data
    assert modifier_from_dict(data) == modifier


def test_a_modifier_is_written_with_its_type_and_only_what_isnt_default():
    assert modifier_to_dict(BLESS) == {
        "type": "D20Bonus",
        "tests": ["attack roll", "saving throw"],
        "amount": "1d4",
    }
    assert modifier_to_dict(ArmorClass(2)) == {"type": "ArmorClass", "bonus": 2}


@pytest.mark.parametrize(
    "data",
    [
        {"tests": ["saving throw"], "amount": "1d4"},  # no type
        {"type": "Bonus", "amount": "1d4"},
        {"type": "ArmorClass", "bonus": 2, "until": "end"},
        {"type": "ArmorClass", "bonus": True},
        {"type": "ArmorClass", "bonus": "2"},
        {"type": "ArmorClass"},
        {"type": "D20Bonus", "tests": ["saving throws"], "amount": "1d4"},
        {"type": "D20Bonus", "tests": "saving throw", "amount": "1d4"},
        {"type": "D20Bonus", "tests": ["saving throw"], "amount": "d4"},
        {"type": "AttacksAgainst", "mode": "Neutral"},
        "ArmorClass(2)",
    ],
)
def test_a_modifier_that_isnt_one_is_refused(data):
    with pytest.raises(ValueError, match="Invalid modifier of Bless"):
        modifier_from_dict(data, "Bless")


# ---------------------------------------------------------------------------
# A badge's modifiers on its CombatCondition


def test_a_condition_keeps_its_modifiers_in_its_data():
    effect = CombatEffect(
        conditions=(CombatCondition("Shield of Faith", modifiers=(ArmorClass(2),)),)
    )
    data = effect.to_dict()
    assert data == {
        "conditions": [
            {
                "name": "Shield of Faith",
                "modifiers": [{"type": "ArmorClass", "bonus": 2}],
            }
        ]
    }
    assert CombatEffect.from_dict(data) == effect


def test_a_condition_from_before_modifiers_has_none():
    effect = CombatEffect.from_dict({"conditions": [{"name": "Bless"}]})
    assert effect.conditions[0].modifiers == ()


def test_a_bad_modifier_in_an_effects_data_says_where():
    data = {"conditions": [{"name": "Bless", "modifiers": [{"type": "Bonus"}]}]}
    with pytest.raises(ValueError, match="Fireball, conditions.0..modifiers.0."):
        CombatEffect.from_dict(data, "Fireball")


@pytest.mark.parametrize(
    "make",
    [
        # A rules condition's modifiers are the rules' (RulesConditions.py).
        lambda: CombatCondition(Condition.PRONE, modifiers=(ArmorClass(2),)),
        lambda: CombatCondition("Restrained by vines", modifiers=(ArmorClass(2),)),
        lambda: CombatCondition(
            "Bless", modifiers=(HasConditions((Condition.PRONE,)),)
        ),
        lambda: CombatCondition("Bless", modifiers=[BLESS]),  # type: ignore[arg-type]
        lambda: CombatCondition("Bless", modifiers=("1d4",)),  # type: ignore[arg-type]
    ],
)
def test_a_condition_with_modifiers_that_cant_be_is_refused(make):
    with pytest.raises(ValueError):
        make()


def test_bless_and_shield_of_faith_say_what_their_badges_do():
    """Bless: "the target adds 1d4 to the attack roll or save". Shield of
    Faith: "a +2 bonus to AC for the duration"."""
    bless = SpellFactory.create("Bless").combat_effects()
    assert badge_modifiers(bless, "Bless") == (BLESS,)
    shield = SpellFactory.create("Shield of Faith").combat_effects()
    assert badge_modifiers(shield, "Shield of Faith") == (ArmorClass(2),)
    assert badge_modifiers(shield, "Bless") == ()
    assert badge_modifiers(None, "Bless") == ()


# ---------------------------------------------------------------------------
# The record


def test_a_record_with_only_modifiers_says_something():
    char = _blessed()
    effect = find_effect(char, "Bless")
    assert effect is not None and says_something(effect)
    assert effect["modifiers"] == [modifier_to_dict(BLESS)]
    assert json.loads(json.dumps(char)) == char


def test_giving_no_modifiers_keeps_those_there_are():
    """A badge given again by hand keeps its spell's modifiers."""
    char = _blessed()
    give_modifiers(char, "Bless", ())
    assert _modifiers(char, "Bless") == [modifier_to_dict(BLESS)]
    give_modifiers(char, "Hexed", ())
    assert find_effect(char, "Hexed") is None


def test_a_record_from_before_modifiers_gets_none_on_a_copy():
    old = {
        "name": "Tiger",
        KEY: [{k: v for k, v in new_effect("Bless").items() if k != "modifiers"}],
    }
    old[KEY][0]["tooltip"] = "card"
    before = json.loads(json.dumps(old))
    assert ending_conditions(old) == set()
    assert old == before, "ending_conditions reads a copy"
    upgraded = upgrade_old_keys(old)
    assert upgraded[KEY] == [{**new_effect("Bless"), "tooltip": "card"}]


# ---------------------------------------------------------------------------
# What the modifiers make of a roll (Combat/Effects/modifiers.py)


def test_an_effects_modifiers_count_while_its_badge_is_on():
    char = _blessed()
    assert modifiers_on(char) == [("Bless", BLESS)]
    char["conditions"].remove("Bless")
    assert modifiers_on(char) == []
    remove_effect(char, "Bless")
    assert modifiers_on(char) == []


def test_bless_adds_1d4_to_a_save_and_its_own_attack_rolls():
    plan = save_plan(_blessed(), "WIS", NEUTRAL)
    assert plan.bonuses == (("Bless", "1d4"),)
    attack = attack_plan(_blessed("Pirate"), _with(), NEUTRAL)
    assert attack.bonuses == (("Pirate's Bless", "1d4"),)
    # Not to attack rolls against the blessed creature.
    assert attack_plan(_with(name="Pirate"), _blessed(), NEUTRAL).bonuses == ()


def test_a_typed_total_gets_no_bonus():
    assert save_plan(_blessed(), "WIS", NEUTRAL, typed=True).bonuses == ()
    assert attack_plan(_blessed("Pirate"), None, NEUTRAL, typed=True).bonuses == ()


def test_exhaustions_bonus_a_level_stays_a_note():
    plan = save_plan(_with("Exhaustion"), "WIS", NEUTRAL)
    assert plan.bonuses == ()
    assert plan.notes == ("Exhaustion (not counted): -2 a level",)


@pytest.mark.parametrize(
    "states, bonuses, ac",
    [
        ([HALF], ((HALF, "2"),), 2),
        ([THREE_QUARTERS], ((THREE_QUARTERS, "5"),), 5),
        # Only the most protective degree, in either order.
        ([HALF, THREE_QUARTERS], ((THREE_QUARTERS, "5"),), 5),
        ([THREE_QUARTERS, HALF], ((THREE_QUARTERS, "5"),), 5),
        ([Visibility.INVISIBLE.value], (), 0),
    ],
)
def test_cover_adds_to_dexterity_saves_and_ac(states, bonuses, ac):
    char = _with(visibility_states=states)
    assert save_plan(char, "DEX", NEUTRAL).bonuses == bonuses
    assert save_plan(char, "WIS", NEUTRAL).bonuses == ()
    assert armor_class_bonus(char) == ac


def test_shield_of_faith_and_cover_add_to_ac():
    char = _with("Shield of Faith", visibility_states=[HALF])
    give_modifiers(char, "Shield of Faith", (ArmorClass(2),))
    assert armor_class_bonus(char) == 4


def test_an_effects_attacks_against_and_resistance_count():
    """What a badge says counts as a rules condition's does (Faerie Fire's
    Advantage, Rage's Resistance), from the effect, not only the table."""
    target = _with("Lit")
    give_modifiers(target, "Lit", (AttacksAgainst(RollMode.ADVANTAGE),))
    plan = attack_plan(_with(name="Pirate"), target, NEUTRAL)
    assert plan.mode == "Advantage"
    assert plan.notes == ("Tiger's Lit: Advantage",)
    raging = _with("Raging")
    give_modifiers(raging, "Raging", (Resistance((DamageType.SLASHING,)),))
    assert resists(raging, DamageType.SLASHING.value)
    assert not resists(raging, DamageType.FIRE.value)


def test_a_rolled_save_adds_blesss_d4_and_says_so(monkeypatch):
    _dice(monkeypatch, d20s=(10, 1), d4s=(3,))
    char = _blessed()
    char["Saving Throws"] = {"WIS": 1}
    result = roll_save(char, "WIS", 14, NEUTRAL)
    assert (result.total, result.success) == (14, True)  # 10 + 1 + 3
    assert result.note == "Bless: +3 (1d4)"


def test_a_typed_save_stays_as_typed(monkeypatch):
    monkeypatch.setattr(random, "randint", lambda *a: pytest.fail("rolled"))
    result = roll_save(_blessed(), "WIS", 14, NEUTRAL, typed=13)
    assert (result.total, result.success, result.note) == (13, False, "")


@pytest.mark.parametrize("states, bonus", [([HALF], 2), ([THREE_QUARTERS], 5)])
def test_a_dexterity_save_behind_cover(monkeypatch, states, bonus):
    _dice(monkeypatch, d20s=(10, 1))
    char = _with(visibility_states=states)
    char["Saving Throws"] = {"DEX": 3}
    result = roll_save(char, "DEX", 15, NEUTRAL)
    assert result.total == 13 + bonus
    assert result.note == f"{states[0]}: +{bonus}"
    _dice(monkeypatch, d20s=(10, 1))
    assert roll_save(char, "WIS", 15, NEUTRAL).total == 10  # only Dexterity


# ---------------------------------------------------------------------------
# In the window


@pytest.fixture(autouse=True)
def no_modal_dialogs(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError(f"unexpected modal dialog: {args[1:3]}")

    monkeypatch.setattr(QDialog, "exec", refuse)
    monkeypatch.setattr(QMessageBox, "warning", refuse)
    monkeypatch.setattr(QMessageBox, "question", refuse)


@pytest.fixture
def fight(tmp_path):
    """A Pirate (15, the source) and a Tiger (10, the target) at AC 15, the
    Tiger with +1 to Wisdom saves and +3 to Dexterity saves."""
    ui = make_ui(tmp_path, [Pirate(), Tiger()])
    pirate, tiger = ui.characters
    for char, value in zip(ui.characters, (15, 10)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    ui._select_target_character(tiger)
    tiger["ac"] = 15
    tiger["Saving Throws"] = {"WIS": 1, "DEX": 3}
    return ui, pirate, tiger


def _log(ui) -> str:
    return str(ui._read_log())


def _bless_pick(**kwargs) -> CustomEffect:
    """Bless as the Custom dialog's pick gives it, cast by nobody in
    particular (so nothing is spent)."""
    option = EffectOption(
        name="Bless",
        kind=SPELL,
        condition="Bless",
        badge_modifiers=(("Bless", (BLESS,)),),
    )
    return CustomEffect(name="Bless", condition="Bless", pick=option, **kwargs)


def _cast_bless(ui, pirate, *targets):
    ui._select_character(pirate)
    ui._set_targets(list(targets))
    ui._apply_cast_spell(SpellFactory.create("Bless"))


def test_cast_spell_puts_blesss_modifiers_on_its_targets(fight):
    ui, pirate, tiger = fight
    _cast_bless(ui, pirate, tiger)
    effect = find_effect(tiger, "Bless")
    assert effect is not None
    assert effect["modifiers"] == [modifier_to_dict(BLESS)]
    assert find_effect(pirate, "Bless") is None


def test_shield_of_faith_cast_gives_its_target_2_ac(fight):
    ui, pirate, tiger = fight
    ui._select_character(pirate)
    ui._apply_cast_spell(SpellFactory.create("Shield of Faith"))
    assert armor_class_bonus(tiger) == 2


def test_a_blessed_targets_rolled_save_adds_1d4_in_the_log(fight, monkeypatch):
    ui, pirate, tiger = fight
    _cast_bless(ui, pirate, tiger)
    ui._select_character(pirate)
    _dice(monkeypatch, d20s=(10, 1), d4s=(3,))
    ui._apply_custom_effect(CustomEffect(name="Sleep", ability="WIS", dc=14))
    assert (
        "Tiger makes a DC 14 Wisdom save against Sleep, rolled 14, Bless: +3 (1d4)"
        in _log(ui)
    )


def test_a_blessed_attackers_roll_adds_1d4_in_the_log(fight, monkeypatch):
    """+5 and an 8 is 13, a miss against AC 15; Bless's 4 makes it 17."""
    ui, pirate, tiger = fight
    _cast_bless(ui, pirate, pirate)
    ui._set_targets([tiger])
    _dice(monkeypatch, d20s=(8, 1), d4s=(4,))
    bolt = CustomEffect(damage=[(20, "Fire")], attack_bonus=5, name="Fire Bolt")
    ui._apply_custom_effect(bolt)
    assert tiger["hp"] == tiger["max_hp"] - 20
    assert "Pirate's attack roll of 17 hits Tiger, Pirate's Bless: +4 (1d4)" in _log(ui)


def test_a_blessed_monsters_action_adds_1d4(fight, monkeypatch):
    from Combat.CombatUIQt.monster_actions import MonsterAction

    ui, pirate, tiger = fight
    _cast_bless(ui, pirate, pirate)
    ui._set_targets([tiger])
    _dice(monkeypatch, d20s=(8, 1), d4s=(2,))
    ui._roll_action(MonsterAction("Bite", "A bite.", to_hit=5), pirate)
    text = ui._action_result_label.text()
    assert "rolled 15 (8+5+2)" in text
    assert "HIT" in text
    assert "Pirate's Bless: +2 (1d4)" in text


def test_shield_of_faith_raises_the_ac_an_attack_is_compared_with(fight, monkeypatch):
    """A 10 + 5 meets AC 15, not 15 + 2."""
    ui, pirate, tiger = fight
    ui._select_character(pirate)
    ui._apply_cast_spell(SpellFactory.create("Shield of Faith"))
    _dice(monkeypatch, d20s=(10, 1))
    ui._apply_custom_effect(
        CustomEffect(damage=[(20, "Fire")], attack_bonus=5, name="Fire Bolt")
    )
    assert tiger["hp"] == tiger["max_hp"]
    assert tiger["ac_above"] == 13, "what the miss showed, without the +2"
    assert ui._target_armor() == 17


def test_the_dialogs_pick_gives_its_badges_modifiers(fight):
    ui, _, tiger = fight
    ui._apply_custom_effect(_bless_pick())
    assert _modifiers(tiger, "Bless") == [modifier_to_dict(BLESS)]


def test_a_badge_typed_over_in_the_dialog_gives_none(fight):
    ui, _, tiger = fight
    effect = _bless_pick()
    effect.condition = "Blessed"
    ui._apply_custom_effect(effect)
    assert "Blessed" in tiger["conditions"]
    assert modifiers_on(tiger) == []


def test_removing_the_badge_by_hand_removes_its_modifier(fight):
    ui, pirate, tiger = fight
    _cast_bless(ui, pirate, tiger)
    ui._remove_condition_from(tiger, "Bless")  # the badge's right-click
    assert find_effect(tiger, "Bless") is None
    assert save_plan(tiger, "WIS", NEUTRAL).bonuses == ()


def test_a_badge_whose_timer_runs_out_takes_its_modifier(fight):
    ui, _, tiger = fight
    ui._apply_custom_effect(_bless_pick(duration={"seconds": 6}))
    assert save_plan(tiger, "WIS", NEUTRAL).bonuses == (("Bless", "1d4"),)
    ui._advance_turn()  # the Tiger's turn
    ui._advance_turn()  # round 2: the round given on the Pirate's turn passes
    assert "Bless" not in tiger["conditions"]
    assert find_effect(tiger, "Bless") is None, "the record goes with its badge"
    assert save_plan(tiger, "WIS", NEUTRAL).bonuses == ()


def test_a_broken_concentration_takes_blesss_modifier(fight):
    ui, pirate, tiger = fight
    _cast_bless(ui, pirate, tiger)
    ui._remove_condition_from(pirate, "Concentrating", source=pirate)
    assert "Bless" not in tiger["conditions"]
    assert find_effect(tiger, "Bless") is None, "the record goes with its badge"
    assert modifiers_on(tiger) == []


def _concentrating_monster(ui, tiger):
    """The Tiger concentrates on a spell (+2 to Constitution saves) and rolls
    its own Concentration saves."""
    ui.settings.monsters_roll_concentration = True
    tiger["Saving Throws"] = {**tiger["Saving Throws"], "CON": 2}
    tiger["conditions"].append("Concentrating")
    tiger["active_spells"] = [
        {"name": "Hold", "time_left": 60, "duration": 60, "concentration": True}
    ]


def test_a_blessed_monsters_concentration_save_adds_1d4(fight, monkeypatch):
    """Concentration is a Constitution saving throw, which Bless adds 1d4 to:
    a 6 + 2 fails DC 10, and Bless's 3 makes it 11 (DI-071)."""
    ui, pirate, tiger = fight
    _cast_bless(ui, pirate, tiger)
    _concentrating_monster(ui, tiger)
    _dice(monkeypatch, d20s=(6,), d4s=(3,))  # a straight roll throws one d20
    ui._ask_concentration_save(tiger, 10)
    assert "Concentrating" in tiger["conditions"]
    assert "Tiger keeps concentration (DC 10, rolled 11, Bless: +3 (1d4))" in _log(ui)


def test_a_monsters_concentration_save_without_bonuses_is_as_before(fight, monkeypatch):
    """One d20 and nothing else: the same dice as before step 3.3."""
    ui, _, tiger = fight
    _concentrating_monster(ui, tiger)
    _dice(monkeypatch, d20s=(6,))
    ui._ask_concentration_save(tiger, 10)
    assert "Concentrating" not in tiger["conditions"]
    assert "Tiger loses concentration (DC 10, rolled 8)" in _log(ui)


def test_an_exhausted_monsters_concentration_save_says_what_isnt_counted(
    fight, monkeypatch
):
    """Exhaustion: "the roll is reduced by 2 times your Exhaustion level";
    the level isn't tracked, so the log says so, as other saves do."""
    ui, _, tiger = fight
    _concentrating_monster(ui, tiger)
    tiger["conditions"].append("Exhaustion")
    _dice(monkeypatch, d20s=(12,))
    ui._ask_concentration_save(tiger, 10)
    assert (
        "Tiger keeps concentration (DC 10, rolled 14,"
        " Exhaustion (not counted): -2 a level)" in _log(ui)
    )


def test_the_bonus_dice_are_rolled_for_each_roll(monkeypatch):
    """Two saves in a row, Bless's d4 a 1 and then a 4: three apart."""
    char = _blessed()
    char["Saving Throws"] = {"WIS": 1}
    _dice(monkeypatch, d20s=(10, 1, 10, 1), d4s=(1, 4))
    first = roll_save(char, "WIS", 30, NEUTRAL)
    second = roll_save(char, "WIS", 30, NEUTRAL)
    assert (first.total, second.total) == (12, 15)
    assert (first.note, second.note) == ("Bless: +1 (1d4)", "Bless: +4 (1d4)")


def test_undo_brings_back_the_modifier(fight):
    ui, pirate, tiger = fight
    _cast_bless(ui, pirate, tiger)
    ui._remove_condition_from(tiger, "Bless")
    ui._undo_last()
    assert modifiers_on(tiger) == [("Bless", BLESS)]


def test_a_typed_attack_roll_stays_as_typed(fight, monkeypatch):
    ui, pirate, tiger = fight
    _cast_bless(ui, pirate, pirate)
    ui._select_character(pirate)
    ui._set_targets([tiger])
    monkeypatch.setattr(random, "randint", lambda *a: pytest.fail("rolled"))
    ui.attack_roll_input.setText("14")
    ui._apply_attack_roll()
    lines = [line for line in _log(ui).split("', '") if "attack roll of 14" in line]
    assert len(lines) == 1 and "misses" in lines[0] and "Bless" not in lines[0]


def _chips(dlg, row: str) -> dict[str, QPushButton]:
    widget = dlg.findChild(QWidget, row)
    return {b.text().replace("&", ""): b for b in widget.findChildren(QPushButton)}


def _infos(dlg) -> list[str]:
    rows = dlg.findChildren(QLabel, "targetRowInfo")
    return [label.text() for label in rows if label.isVisibleTo(dlg)]


def _tooltips(dlg) -> list[str]:
    rows = dlg.findChildren(QLabel, "targetRowInfo")
    return [label.toolTip() for label in rows if label.isVisibleTo(dlg)]


def test_the_dialog_reminds_of_the_bonus_for_a_roll_at_the_table(fight, monkeypatch):
    ui, pirate, tiger = fight
    _cast_bless(ui, pirate, pirate, tiger)
    ui._select_character(pirate)
    ui._set_targets([tiger])
    tiger["visibility_states"] = [HALF]
    monkeypatch.undo()  # the dialog's exec, for open_dialog
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _chips(dlg, "saveAbilityButtons")["WIS"].click()
    assert _infos(dlg) == ["WIS +1 +1d4"]
    assert "Bless: +1d4" in _tooltips(dlg)[0]
    _chips(dlg, "saveAbilityButtons")["DEX"].click()
    assert _infos(dlg) == ["DEX +5 +1d4 (cover)"]
    assert "Half Cover: +2" in _tooltips(dlg)[0]
    _chips(dlg, "rollKindButtons")[ATTACK_ROLL].click()
    assert _infos(dlg) == ["AC 17 (cover), +1d4 to hit"]
    assert "Pirate's Bless: +1d4" in _tooltips(dlg)[0]


def test_shield_of_faith_shows_in_the_dialogs_ac(fight, monkeypatch):
    ui, pirate, tiger = fight
    ui._select_character(pirate)
    ui._apply_cast_spell(SpellFactory.create("Shield of Faith"))
    monkeypatch.undo()
    dlg = open_dialog(monkeypatch, ui._show_custom_condition_dialog)
    _chips(dlg, "rollKindButtons")[ATTACK_ROLL].click()
    assert _infos(dlg) == ["AC 17"]
    assert "Shield of Faith: +2 AC" in _tooltips(dlg)[0]
