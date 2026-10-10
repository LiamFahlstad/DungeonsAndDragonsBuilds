"""Each part works out its own final values from nothing but a CharacterView
(Notes/model-refactor-plan.md, Step 6). These run against FakeView: no
builder, no Character. Expected values come from the 2024 PHB rules.
"""

from Core.Definitions import (
    Ability,
    ArmorType,
    CharacterClass,
    DiceRollCondition,
)
from Core.SpellcastingRules import CasterType
from Model.Ledger.ArmorClass import ArmorClass, ArmorClassFormula
from Model.ClassLevels import ClassLevels
from Model.Ledger.Ledger import Ledger
from Model.Ledger.Initiative import Initiative
from Model.Ledger.SavingThrows import SavingThrows
from Model.Ledger.Spellcasting import Spellcasting
from tests._fake_view import FakeView

ADV = DiceRollCondition.ADVANTAGE
DIS = DiceRollCondition.DISADVANTAGE
NEUTRAL = DiceRollCondition.NEUTRAL


class TestSavingThrows:
    def test_modifier_adds_proficiency_only_when_proficient(self):
        saves = SavingThrows()
        saves.add_proficiency(Ability.WISDOM)
        saves.add_bonus(Ability.WISDOM, 1)
        view = FakeView({Ability.WISDOM: 16, Ability.DEXTERITY: 14})
        assert saves.modifier(Ability.WISDOM, view) == 3 + 2 + 1
        assert saves.modifier(Ability.DEXTERITY, view) == 2

    def test_untrained_armor_cancels_advantage_on_dexterity_saves(self):
        saves = SavingThrows()
        saves.add_advantage(Ability.DEXTERITY)
        saves.add_advantage(Ability.WISDOM)
        view = FakeView(untrained_armor=True)
        assert saves.roll_condition(Ability.DEXTERITY, view) == NEUTRAL
        assert saves.roll_condition(Ability.WISDOM, view) == ADV


class TestInitiative:
    def test_total_is_dexterity_plus_proficiency_plus_bonuses(self):
        initiative = Initiative()
        initiative.add_proficiency()
        initiative.add_bonus(1)
        view = FakeView({Ability.DEXTERITY: 16}, proficiency_bonus=3)
        assert initiative.total(view) == 3 + 3 + 1

    def test_untrained_armor_imposes_disadvantage(self):
        assert Initiative().roll_condition(FakeView(untrained_armor=True)) == DIS
        initiative = Initiative()
        initiative.add_roll_condition(ADV)
        assert initiative.roll_condition(FakeView(untrained_armor=True)) == NEUTRAL


class TestArmorClass:
    def test_a_shield_counts_only_with_training(self):
        armor_class = ArmorClass()
        armor_class.add_shield_bonus(2)
        dexterity = {Ability.DEXTERITY: 14}
        untrained = FakeView(dexterity, is_wielding_shield=True)
        trained = FakeView(dexterity, is_wielding_shield=True, has_shield_training=True)
        assert armor_class.total(untrained) == 12
        assert armor_class.total(trained) == 14

    def test_ignore_shield_brings_back_unarmored_defense(self):
        # Monk's Unarmored Defense: 10 + DEX + WIS, only without a Shield.
        armor_class = ArmorClass()
        armor_class.add_armor_class_formula(
            ArmorClassFormula(
                10,
                frozenset({Ability.DEXTERITY, Ability.WISDOM}),
                allows_shield=False,
            )
        )
        armor_class.add_shield_bonus(2)
        view = FakeView(
            {Ability.DEXTERITY: 16, Ability.WISDOM: 16},
            is_wielding_shield=True,
            has_shield_training=True,
        )
        assert armor_class.total(view) == 10 + 3 + 2  # plain 10 + DEX, + Shield
        assert armor_class.total(view, ignore_shield=True) == 10 + 3 + 3


class TestSpellcasting:
    def test_difficulty_class_and_attack_bonus(self):
        spellcasting = Spellcasting()
        spellcasting.add_spell_save_dc_bonus(1)
        view = FakeView({Ability.INTELLIGENCE: 18}, proficiency_bonus=3)
        assert (
            spellcasting.difficulty_class(Ability.INTELLIGENCE, view) == 8 + 3 + 4 + 1
        )
        assert spellcasting.attack_bonus(Ability.INTELLIGENCE, view) == 3 + 4

    def test_spell_slots_from_registered_casters(self):
        spellcasting = Spellcasting()
        spellcasting.register_caster(CharacterClass.WIZARD, CasterType.FULL_CASTER)
        view = FakeView(
            class_levels=ClassLevels(
                base_class=CharacterClass.WIZARD,
                level_per_class={CharacterClass.WIZARD: 3},
            )
        )
        # PHB Wizard table, level 3: four 1st-level and two 2nd-level slots.
        assert spellcasting.spell_slots(view) == {1: 4, 2: 2}


class TestLedgerArmorRules:
    def test_untrained_body_armor(self):
        ledger = Ledger()
        ledger.worn_armor.set_body_armor(ArmorType.HEAVY, "Plate")
        assert ledger.is_wearing_untrained_armor()
        assert ledger.has_untrained_armor_disadvantage(Ability.STRENGTH)
        assert not ledger.has_untrained_armor_disadvantage(Ability.WISDOM)
        assert len(ledger.armor_warnings()) == 1

    def test_trained_armor_has_no_warnings(self):
        ledger = Ledger()
        ledger.worn_armor.set_body_armor(ArmorType.HEAVY, "Plate")
        ledger.equipment_training.add_armor_training(ArmorType.HEAVY)
        assert not ledger.is_wearing_untrained_armor()
        assert ledger.armor_warnings() == []

    def test_untrained_shield_warns(self):
        ledger = Ledger()
        ledger.worn_armor.wield_shield()
        assert not ledger.has_shield_training()
        assert ledger.armor_warnings() == [
            "Wielding a Shield without Shield training: it grants no AC bonus."
        ]
