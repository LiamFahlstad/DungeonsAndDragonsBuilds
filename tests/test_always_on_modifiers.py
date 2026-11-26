"""Always-on modifiers (Notes/combat-effects-plan.md, step 9.2): what a
creature has all the time counts in the saving throws the simulator rolls,
as a badge's modifiers do while it's on. A player's features say theirs
(Feature.combat_modifiers), a stat block's traits theirs by name
(TRAIT_MODIFIERS), and a save is told what it's against (SaveAgainst), which
settles those that count only against some.

Expected values are the rules text's:

- Magic Resistance (Monster Manual 2024): "Advantage on saving throws
  against spells and other magical effects."
- Brave (Halfling): "Advantage on saving throws you make to avoid or end
  the Frightened condition." Fey Ancestry (Charmed) and Dwarven Resilience
  (Poisoned) say the same of theirs.
- War Caster: "Advantage on Constitution saving throws that you make to
  maintain Concentration."
- Danger Sense (Barbarian 2): "Advantage on Dexterity saving throws unless
  you have the Incapacitated condition."
- Gnomish Cunning: "Advantage on Intelligence, Wisdom, and Charisma saving
  throws." Dual Mind (Kalashtar): Wisdom and Charisma.
- Rules Glossary, Advantage: "If circumstances cause a roll to have both
  Advantage and Disadvantage, you don't have either of them."
"""

import random
from typing import cast

import pytest
from PyQt6.QtWidgets import QDialog, QMessageBox

from CharacterContent.Features.CharacterFeats.GeneralFeats import WarCaster
from CharacterContent.Features.ClassFeatures.Barbarian.BarbarianFeatures import (
    DangerSenseText,
)
from CharacterContent.Features.SpeciesFeatures import ElfFeatures, KhoravarFeatures
from CharacterContent.Features.SpeciesFeatures.DwarfFeatures import (
    DwarvenResilience,
)
from CharacterContent.Features.SpeciesFeatures.GnomeFeatures import GnomishCunning
from CharacterContent.Features.SpeciesFeatures.HalflingFeatures import Brave
from CharacterContent.Features.SpeciesFeatures.KalashtarFeatures import DualMind
from Combat.Combatants import Pirate, Tiger
from Combat.Effects.active_effects import repeat_saves
from Combat.Effects.always_on import (
    KEEPS_CONCENTRATION,
    SaveAgainst,
    always_on_modifiers,
)
from Combat.Effects.modifiers import held_conditions
from Combat.Effects.roll_plans import save_plan
from Combat.Fight.saves import (
    FEATURE,
    SPELL,
    CustomEffect,
    EffectOption,
    roll_save,
    save_against,
)
from Core.Definitions import Ability, Condition
from Model.Content.CombatModifiers import (
    D20Mode,
    D20Test,
    RollMode,
    modifier_from_dict,
    modifier_to_dict,
)
from Model.Creatures.MonsterAbilities import MagicResistance
from tests._combat_ui import make_ui

NEUTRAL, ADVANTAGE = "Neutral", "Advantage"
SPELL_SAVE = SaveAgainst(spell=True)
FEATURE_SAVE = SaveAgainst(spell=False)


def _monster(*traits, conditions=()) -> dict:
    return {"name": "Mage", "conditions": list(conditions), "traits": list(traits)}


def _player(*features, conditions=()) -> dict:
    return {
        "name": "Clover",
        "conditions": list(conditions),
        "_feature_objects": list(features),
    }


def _mode(char: dict, ability: str, against: SaveAgainst | None) -> str:
    return save_plan(char, ability, NEUTRAL, against=against).mode


# ---------------------------------------------------------------------------
# The model


@pytest.mark.parametrize(
    "modifier",
    [
        D20Mode((D20Test.SAVING_THROW,), RollMode.ADVANTAGE, against_spells=True),
        D20Mode(
            (D20Test.SAVING_THROW,),
            RollMode.ADVANTAGE,
            against_conditions=(Condition.FRIGHTENED, Condition.CHARMED),
        ),
        D20Mode(
            (D20Test.SAVING_THROW,),
            RollMode.ADVANTAGE,
            (Ability.CONSTITUTION,),
            concentration=True,
        ),
        D20Mode(
            (D20Test.SAVING_THROW,),
            RollMode.ADVANTAGE,
            (Ability.DEXTERITY,),
            unless_conditions=(Condition.INCAPACITATED,),
        ),
    ],
)
def test_a_save_gate_reads_back_as_it_was_written(modifier):
    assert modifier_from_dict(modifier_to_dict(modifier)) == modifier


@pytest.mark.parametrize(
    "make",
    [
        lambda: D20Mode(
            (D20Test.ATTACK_ROLL,), RollMode.ADVANTAGE, against_spells=True
        ),
        lambda: D20Mode(
            (D20Test.SAVING_THROW, D20Test.ABILITY_CHECK),
            RollMode.ADVANTAGE,
            against_conditions=(Condition.FRIGHTENED,),
        ),
        lambda: D20Mode(
            (D20Test.SAVING_THROW,),
            RollMode.ADVANTAGE,
            (Ability.DEXTERITY,),
            concentration=True,
        ),
    ],
)
def test_a_save_gate_on_anything_but_a_save_is_refused(make):
    with pytest.raises(ValueError):
        make()


def test_a_feature_changes_no_roll_unless_it_says_so():
    from Model.Content.Feature import Feature
    from Model.View import CharacterView

    feature = Feature(name="Anything", origin="Test")
    assert feature.combat_modifiers(cast(CharacterView, None)) == ()


# ---------------------------------------------------------------------------
# Magic Resistance


@pytest.mark.parametrize(
    "trait",
    [
        MagicResistance(creature_name="mage"),
        # A generated stat block's text, and a saved log's dict.
        {"name": "Magic Resistance", "description": "The imp has Advantage ..."},
    ],
)
def test_magic_resistance_gives_advantage_on_a_save_against_a_spell(trait):
    plan = save_plan(_monster(trait), "WIS", NEUTRAL, against=SPELL_SAVE)
    assert plan.mode == ADVANTAGE
    assert plan.notes == ("Magic Resistance: Advantage",)


def test_magic_resistance_against_something_else_is_the_gms_to_judge():
    """ "Other magical effects" count too, which only the GM can tell: a
    feature's or a monster's ability may be magical."""
    plan = save_plan(_monster(MagicResistance()), "WIS", NEUTRAL, against=FEATURE_SAVE)
    assert plan.mode == NEUTRAL
    assert plan.notes == (
        "Magic Resistance (not counted): Advantage if the effect is magical",
    )


def test_magic_resistance_with_nothing_known_about_the_save_is_noted():
    plan = save_plan(_monster(MagicResistance()), "WIS", NEUTRAL)
    assert plan.mode == NEUTRAL
    assert plan.notes == (
        "Magic Resistance (not counted): Advantage if the save is against a"
        " spell or other magical effect",
    )


def test_magic_resistance_and_disadvantage_cancel_out():
    """Restrained: Disadvantage on Dexterity saving throws."""
    char = _monster(MagicResistance(), conditions=["Restrained"])
    assert _mode(char, "DEX", SPELL_SAVE) == NEUTRAL
    assert _mode(char, "WIS", SPELL_SAVE) == ADVANTAGE


def test_a_monster_without_the_trait_gets_nothing():
    char = _monster({"name": "Pack Tactics", "description": "..."})
    assert always_on_modifiers(char, held_conditions(char)) == []
    assert _mode(char, "WIS", SPELL_SAVE) == NEUTRAL


def test_a_rolled_save_against_a_spell_takes_the_higher_d20(monkeypatch):
    d20s = iter((4, 17))
    monkeypatch.setattr(random, "randint", lambda low, high: next(d20s))
    char = _monster(MagicResistance())
    char["Saving Throws"] = {"WIS": 2}
    result = roll_save(char, "WIS", 15, NEUTRAL, against=SPELL_SAVE)
    assert (result.total, result.success) == (19, True)
    assert result.note == "Magic Resistance: Advantage"


# ---------------------------------------------------------------------------
# Saves to avoid or end a condition


@pytest.mark.parametrize(
    "feature, condition, other",
    [
        (Brave(), "Frightened", "Charmed"),
        (ElfFeatures.FeyAncestry(), "Charmed", "Frightened"),
        (KhoravarFeatures.FeyAncestry(), "Charmed", "Frightened"),
        (DwarvenResilience(), "Poisoned", "Paralyzed"),
    ],
)
def test_advantage_on_saves_to_avoid_or_end_one_condition(feature, condition, other):
    char = _player(feature)
    # To avoid it: a save against an effect that gives it, alone or with more.
    assert _mode(char, "WIS", SaveAgainst(True, (condition,))) == ADVANTAGE
    assert _mode(char, "CON", SaveAgainst(False, ("Prone", condition))) == ADVANTAGE
    # Not a save against anything else.
    assert _mode(char, "WIS", SaveAgainst(True, (other,))) == NEUTRAL
    assert _mode(char, "WIS", SaveAgainst(True)) == NEUTRAL
    # Not known: the GM's to judge.
    plan = save_plan(char, "WIS", NEUTRAL)
    assert plan.mode == NEUTRAL
    assert plan.notes == (
        f"{feature.name} (not counted): Advantage if the save is to avoid or"
        f" end the {condition} condition",
    )


def test_save_against_reads_the_conditions_an_effect_gives():
    against = save_against(None, "Frightened + Incapacitated")
    assert against == SaveAgainst(None, ("Frightened", "Incapacitated"))


# ---------------------------------------------------------------------------
# War Caster


def test_war_caster_gives_advantage_on_a_concentration_save():
    char = _player(WarCaster(4, Ability.INTELLIGENCE))
    plan = save_plan(char, "CON", NEUTRAL, against=KEEPS_CONCENTRATION)
    assert (plan.mode, plan.notes) == (ADVANTAGE, ("War Caster: Advantage",))


def test_war_caster_gives_nothing_on_any_other_save():
    char = _player(WarCaster(4, Ability.INTELLIGENCE))
    assert _mode(char, "CON", SPELL_SAVE) == NEUTRAL
    assert _mode(char, "WIS", KEEPS_CONCENTRATION) == NEUTRAL


# ---------------------------------------------------------------------------
# Advantage on saves of some abilities


def test_danger_sense_gives_advantage_on_dexterity_saves():
    char = _player(DangerSenseText())
    assert _mode(char, "DEX", FEATURE_SAVE) == ADVANTAGE
    assert _mode(char, "DEX", None) == ADVANTAGE  # it asks nothing of the save
    assert _mode(char, "WIS", FEATURE_SAVE) == NEUTRAL


@pytest.mark.parametrize("held", ["Incapacitated", "Stunned"])
def test_danger_sense_is_lost_while_incapacitated(held):
    """Stunned gives Incapacitated, and with it the exception."""
    char = _player(DangerSenseText(), conditions=[held])
    assert always_on_modifiers(char, held_conditions(char)) == []


@pytest.mark.parametrize(
    "feature, abilities",
    [
        (GnomishCunning(), ("INT", "WIS", "CHA")),
        (DualMind(), ("WIS", "CHA")),
    ],
)
def test_advantage_on_saves_of_these_abilities(feature, abilities):
    char = _player(feature)
    for ability in ("STR", "DEX", "CON", "INT", "WIS", "CHA"):
        expected = ADVANTAGE if ability in abilities else NEUTRAL
        assert _mode(char, ability, SPELL_SAVE) == expected, ability


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
    """A Pirate (the source) and a Tiger with Magic Resistance (the
    target), +1 to Wisdom saves."""
    ui = make_ui(tmp_path, [Pirate(), Tiger()])
    pirate, tiger = ui.characters
    for char, value in zip(ui.characters, (15, 10)):
        ui._initiative_inputs[id(char)].setText(str(value))
    ui._start_combat()
    ui._select_character(pirate)
    ui._select_target_character(tiger)
    tiger["Saving Throws"] = {"WIS": 1}
    tiger["traits"] = [*(tiger.get("traits") or []), MagicResistance()]
    return ui, pirate, tiger


def _d20s(monkeypatch, *rolls):
    d20s = iter(rolls)
    monkeypatch.setattr(random, "randint", lambda low, high: next(d20s))


def _save_effect(kind: str, **pick) -> CustomEffect:
    option = EffectOption(name="Hold", kind=kind, **pick)
    return CustomEffect(name="Hold", ability="WIS", dc=14, pick=option)


def test_the_dialogs_save_against_a_spell_counts_magic_resistance(fight, monkeypatch):
    ui, _, tiger = fight
    _d20s(monkeypatch, 3, 15)
    ui._apply_custom_effect(_save_effect(SPELL, spell_name="Hold Person"))
    assert (
        "Tiger makes a DC 14 Wisdom save against Hold, rolled 16,"
        " Magic Resistance: Advantage" in str(ui._read_log())
    )


def test_the_dialogs_save_against_a_feature_only_notes_it(fight, monkeypatch):
    ui, _, tiger = fight
    _d20s(monkeypatch, 3, 15)
    ui._apply_custom_effect(_save_effect(FEATURE))
    assert (
        "Tiger fails a DC 14 Wisdom save against Hold, rolled 4,"
        " Magic Resistance (not counted): Advantage if the effect is magical"
        in str(ui._read_log())
    )


def test_a_repeat_save_to_end_a_spells_condition_counts_it(fight, monkeypatch):
    """Hold Person's save at the end of each turn is against the spell."""
    ui, _, tiger = fight
    _d20s(monkeypatch, 1, 1)
    ui._apply_custom_effect(
        CustomEffect(
            name="Hold Person",
            condition="Paralyzed",
            ability="WIS",
            dc=14,
            repeat_save=True,
        )
    )
    assert "Paralyzed" in tiger["conditions"]
    (entry,) = repeat_saves(tiger)
    _d20s(monkeypatch, 3, 15)
    ui._roll_repeat_save(tiger, entry, "Wisdom")
    assert "Paralyzed" not in tiger["conditions"]
    assert "Magic Resistance: Advantage" in str(ui._read_log())


def test_a_monsters_concentration_save_counts_war_caster(fight, monkeypatch):
    """A Concentration save is a Constitution saving throw: 6 + 2 fails DC
    10, the higher d20 of 6 and 12 keeps it. Whether the damage's source
    makes it a save against a magical effect is the GM's to judge, so the
    Tiger's Magic Resistance is noted, not counted."""
    ui, _, tiger = fight
    ui.settings.monsters_roll_concentration = True
    tiger["Saving Throws"] = {"CON": 2}
    tiger["_feature_objects"] = [WarCaster(4, Ability.WISDOM)]
    tiger["conditions"].append("Concentrating")
    tiger["active_spells"] = [
        {"name": "Hold", "time_left": 60, "duration": 60, "concentration": True}
    ]
    _d20s(monkeypatch, 6, 12)
    ui._ask_concentration_save(tiger, 10)
    assert "Concentrating" in tiger["conditions"]
    assert (
        "Tiger keeps concentration (DC 10, rolled 14, War Caster: Advantage,"
        " Magic Resistance (not counted): Advantage if the effect is magical)"
        in str(ui._read_log())
    )
