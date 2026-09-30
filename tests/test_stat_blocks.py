"""
Tests for StatBlocks - core data structures for character attributes.
"""

import pytest
from Core.Definitions import (
    Ability,
    Skill,
    CharacterClass,
    DiceRollCondition,
)
from StatBlocks.AbilityScores import (
    AbilityScores,
    StandardArrayAbilityScores,
    PointBuyAbilityScores,
)
from StatBlocks.Skills import Skills
from StatBlocks.SavingThrows import SavingThrows
from StatBlocks.ArmorClass import UNARMORED_ARMOR_CLASS, ArmorClass, ArmorClassFormula
from StatBlocks.ClassLevels import ClassLevels
from StatBlocks.HitPoints import HitPoints


class TestAbilityScores:
    """Test AbilityScores for ability scores and modifiers."""

    def test_create_abilities_stat_block(self, standard_abilities):
        """Test creating an abilities stat block."""
        assert standard_abilities.strength == 15
        assert standard_abilities.dexterity == 14
        assert standard_abilities.constitution == 13
        assert standard_abilities.intelligence == 12
        assert standard_abilities.wisdom == 10
        assert standard_abilities.charisma == 8

    def test_get_score(self, standard_abilities):
        """Test get_score method."""
        assert standard_abilities.get_score(Ability.STRENGTH) == 15
        assert standard_abilities.get_score(Ability.DEXTERITY) == 14
        assert standard_abilities.get_score(Ability.WISDOM) == 10

    def test_get_modifier(self, standard_abilities):
        """Test ability modifier calculation: (score - 10) // 2."""
        assert standard_abilities.get_modifier(Ability.STRENGTH) == 2  # (15-10)//2 = 2
        assert standard_abilities.get_modifier(Ability.DEXTERITY) == 2  # (14-10)//2 = 2
        assert (
            standard_abilities.get_modifier(Ability.CONSTITUTION) == 1
        )  # (13-10)//2 = 1
        assert (
            standard_abilities.get_modifier(Ability.INTELLIGENCE) == 1
        )  # (12-10)//2 = 1
        assert standard_abilities.get_modifier(Ability.WISDOM) == 0  # (10-10)//2 = 0
        assert standard_abilities.get_modifier(Ability.CHARISMA) == -1  # (8-10)//2 = -1

    def test_add_bonus(self, standard_abilities):
        """Test adding bonuses to ability scores."""
        original_strength = standard_abilities.strength
        standard_abilities.add_bonus(Ability.STRENGTH, 2)
        assert standard_abilities.strength == original_strength + 2
        assert standard_abilities.get_modifier(Ability.STRENGTH) == 3

    def test_add_negative_bonus(self, standard_abilities):
        """Test subtracting from ability scores with negative bonuses."""
        original_charisma = standard_abilities.charisma
        standard_abilities.add_bonus(Ability.CHARISMA, -2)
        assert standard_abilities.charisma == original_charisma - 2
        assert standard_abilities.get_modifier(Ability.CHARISMA) == -2

    def test_add_bonus_invalid_type(self, standard_abilities):
        """Test that add_bonus rejects non-integer bonuses."""
        with pytest.raises(ValueError, match="Bonus must be an integer"):
            standard_abilities.add_bonus(Ability.STRENGTH, "2")

    def test_get_ability_with_highest_modifier(self, standard_abilities):
        """Test finding the ability with highest modifier."""
        # Standard array: STR=2, DEX=2, CON=1, INT=1, WIS=0, CHA=-1
        # Should return STR or DEX (both have +2)
        highest = standard_abilities.get_ability_with_highest_modifier()
        assert highest in [Ability.STRENGTH, Ability.DEXTERITY]

    def test_get_spell_casting_ability_with_highest_modifier(self, standard_abilities):
        """Test finding the spell-casting ability with highest modifier."""
        # INT=1, WIS=0, CHA=-1 -> should be INT
        highest_caster = (
            standard_abilities.get_spell_casting_ability_with_highest_modifier()
        )
        assert highest_caster == Ability.INTELLIGENCE

    def test_extreme_ability_scores(self):
        """Test extreme ability score calculations (very low and very high)."""
        extreme = AbilityScores(
            strength=3,
            dexterity=20,
            constitution=8,
            intelligence=18,
            wisdom=10,
            charisma=15,
        )
        assert extreme.get_modifier(Ability.STRENGTH) == -4  # (3-10)//2 = -4
        assert extreme.get_modifier(Ability.DEXTERITY) == 5  # (20-10)//2 = 5
        assert extreme.get_modifier(Ability.INTELLIGENCE) == 4  # (18-10)//2 = 4


class TestStandardArrayAbilityScores:
    """Test StandardArrayAbilityScores validation."""

    def test_valid_standard_array(self):
        """Test that standard array (15,14,13,12,10,8) is valid."""
        standard = StandardArrayAbilityScores(
            strength=15,
            dexterity=14,
            constitution=13,
            intelligence=12,
            wisdom=10,
            charisma=8,
        )
        assert standard.strength == 15

    def test_valid_standard_array_different_order(self):
        """Test that standard array works in any order."""
        standard = StandardArrayAbilityScores(
            strength=8,
            dexterity=10,
            constitution=12,
            intelligence=13,
            wisdom=14,
            charisma=15,
        )
        assert standard.strength == 8
        assert standard.charisma == 15

    def test_invalid_standard_array_wrong_values(self):
        """Test that non-standard values are rejected."""
        with pytest.raises(ValueError, match="standard array values"):
            StandardArrayAbilityScores(
                strength=16,  # Not in standard array
                dexterity=14,
                constitution=13,
                intelligence=12,
                wisdom=10,
                charisma=8,
            )

    def test_invalid_standard_array_duplicate(self):
        """Test that duplicates in standard array are rejected."""
        with pytest.raises(ValueError, match="standard array values"):
            StandardArrayAbilityScores(
                strength=15,
                dexterity=15,  # Duplicate
                constitution=13,
                intelligence=12,
                wisdom=10,
                charisma=8,
            )


class TestPointBuyAbilityScores:
    """Test PointBuyAbilityScores with point buy validation."""

    def test_valid_point_buy(self):
        """Test a valid point buy configuration."""
        # Starting scores: 8,8,8,8,8,8 (free)
        # 8->10 (2), 8->12 (4), 8->13 (5), 8->14 (7), 8->15 (9) = 27 points
        point_buy = PointBuyAbilityScores(
            strength=15,
            dexterity=14,
            constitution=13,
            intelligence=12,
            wisdom=10,
            charisma=8,
        )
        assert point_buy.strength == 15

    def test_point_buy_score_too_low(self):
        """Test that point buy rejects scores below 8."""
        with pytest.raises(ValueError, match="must be between 8 and 15"):
            PointBuyAbilityScores(
                strength=7,  # Below 8
                dexterity=10,
                constitution=10,
                intelligence=10,
                wisdom=10,
                charisma=10,
            )

    def test_point_buy_score_too_high(self):
        """Test that point buy rejects scores above 15."""
        with pytest.raises(ValueError, match="must be between 8 and 15"):
            PointBuyAbilityScores(
                strength=16,  # Above 15
                dexterity=10,
                constitution=10,
                intelligence=10,
                wisdom=10,
                charisma=10,
            )

    def test_point_buy_wrong_total(self):
        """Test that point buy rejects configurations that don't spend exactly 27 points."""
        with pytest.raises(ValueError, match="spend exactly 27 points"):
            PointBuyAbilityScores(
                strength=15,
                dexterity=15,
                constitution=15,
                intelligence=15,
                wisdom=8,
                charisma=8,
            )


class TestSkills:
    """Test Skills for skill proficiencies and bonuses."""

    def test_create_empty_skills(self, basic_skills):
        """Test creating an empty skills stat block."""
        assert not basic_skills.is_proficient(Skill.ACROBATICS)
        assert not basic_skills.has_expertise(Skill.ACROBATICS)

    def test_add_skill_proficiency(self, basic_skills):
        """Test adding a skill proficiency."""
        basic_skills.add_skill_proficiency(Skill.ACROBATICS)
        assert basic_skills.is_proficient(Skill.ACROBATICS)

    def test_expertise_without_proficiency_fails_validation(self, basic_skills):
        """Expertise without proficiency is rejected once validated."""
        basic_skills.add_skill_expertise(Skill.ACROBATICS)
        with pytest.raises(ValueError, match="unproficient skill"):
            basic_skills.validate()

    def test_expertise_before_proficiency_is_valid(self, basic_skills):
        """The proficiency may be granted after the expertise."""
        basic_skills.add_skill_expertise(Skill.ARCANA)
        basic_skills.add_skill_proficiency(Skill.ARCANA)
        basic_skills.validate()
        assert basic_skills.has_expertise(Skill.ARCANA)

    def test_add_skill_expertise_with_proficiency(self, basic_skills):
        """Test adding expertise after proficiency."""
        basic_skills.add_skill_proficiency(Skill.ARCANA)
        basic_skills.add_skill_expertise(Skill.ARCANA)
        assert basic_skills.has_expertise(Skill.ARCANA)
        assert basic_skills.is_proficient(Skill.ARCANA)

    def test_add_skill_bonus(self, basic_skills):
        """Test adding skill bonuses."""
        basic_skills.add_skill_bonus(Skill.ARCANA, 2)
        assert basic_skills.get_total_bonus(Skill.ARCANA, None) == 2

    def test_add_multiple_skill_bonuses(self, basic_skills):
        """Test that multiple bonuses to the same skill stack."""
        basic_skills.add_skill_bonus(Skill.ARCANA, 2, "Source 1")
        basic_skills.add_skill_bonus(Skill.ARCANA, 3, "Source 2")
        assert basic_skills.get_total_bonus(Skill.ARCANA, None) == 5

    def test_get_all_bonus_sources(self, basic_skills):
        """Test retrieving bonus sources."""
        basic_skills.add_skill_bonus(Skill.ARCANA, 2, "Magic Item")
        basic_skills.add_skill_bonus(Skill.ARCANA, 1, "Feat")
        sources = basic_skills.get_all_bonus_sources(Skill.ARCANA, None)
        assert len(sources) == 2
        assert (2, "Magic Item") in sources
        assert (1, "Feat") in sources

    def test_skill_to_ability_mapping(self, basic_skills):
        """Test that default skill-to-ability mapping is correct."""
        assert basic_skills.get_skill_ability(Skill.ACROBATICS) == Ability.DEXTERITY
        assert basic_skills.get_skill_ability(Skill.ARCANA) == Ability.INTELLIGENCE
        assert basic_skills.get_skill_ability(Skill.ATHLETICS) == Ability.STRENGTH
        assert basic_skills.get_skill_ability(Skill.INSIGHT) == Ability.WISDOM
        assert basic_skills.get_skill_ability(Skill.DECEPTION) == Ability.CHARISMA

    def test_update_skill_to_ability(self, basic_skills):
        """Test changing a skill's linked ability."""
        basic_skills.update_skill_to_ability(Skill.ARCANA, Ability.WISDOM)
        assert basic_skills.get_skill_ability(Skill.ARCANA) == Ability.WISDOM

    def test_reset_skill_to_ability(self, basic_skills):
        """Test resetting a skill's linked ability to default."""
        basic_skills.update_skill_to_ability(Skill.ARCANA, Ability.WISDOM)
        basic_skills.reset_skill_to_ability(Skill.ARCANA)
        assert basic_skills.get_skill_ability(Skill.ARCANA) == Ability.INTELLIGENCE


class TestArmorClass:
    """Test ArmorClass for AC formulas."""

    def test_default_armor_class_formula(self, basic_armor_class):
        """Without armor or features: 10 + Dexterity modifier."""
        assert basic_armor_class.armor_class_formulas == [UNARMORED_ARMOR_CLASS]
        assert UNARMORED_ARMOR_CLASS.base == 10
        assert UNARMORED_ARMOR_CLASS.abilities == {Ability.DEXTERITY}

    def test_add_bonus(self, basic_armor_class):
        """Test adding a flat AC bonus."""
        basic_armor_class.add_bonus(2)
        assert basic_armor_class.bonuses.total(None) == 2

    def test_added_formulas_are_kept_not_overwritten(self, basic_armor_class):
        unarmored = ArmorClassFormula(10, frozenset({Ability.CONSTITUTION}))
        basic_armor_class.add_armor_class_formula(unarmored)
        assert basic_armor_class.get_applicable_armor_class_formulas(False) == [
            UNARMORED_ARMOR_CLASS,
            unarmored,
        ]

    def test_worn_armor_replaces_unarmored_formulas(self, basic_armor_class):
        armor = ArmorClassFormula(18, frozenset(), is_armor=True)
        basic_armor_class.add_armor_class_formula(armor)
        basic_armor_class.add_armor_class_formula(
            ArmorClassFormula(10, frozenset({Ability.WISDOM}))
        )
        assert basic_armor_class.get_applicable_armor_class_formulas(False) == [armor]

    def test_shield_disables_formulas_that_forbid_it(self, basic_armor_class):
        no_shield = ArmorClassFormula(
            10, frozenset({Ability.WISDOM}), allows_shield=False
        )
        basic_armor_class.add_armor_class_formula(no_shield)
        assert no_shield in basic_armor_class.get_applicable_armor_class_formulas(False)
        assert no_shield not in basic_armor_class.get_applicable_armor_class_formulas(
            True
        )


class TestCarryingCapacity:
    """Test CarryingCapacity sources and totals."""

    def test_carrying_capacity_sources(self, basic_carrying_capacity):
        basic_carrying_capacity.add_bonus("Backpack", 2)
        assert basic_carrying_capacity.sources(strength_modifier=1) == [
            ("Person", 4),
            ("Backpack", 2),
        ]
        assert basic_carrying_capacity.total(strength_modifier=1) == 6


class TestHitPoints:
    """Test HitPoints.calculate for hit point rolls."""

    def test_calculate_hit_points_single_class(self, standard_abilities):
        """Test hit point calculation for single-class character."""
        # Wizard level 1: 6 (d6) + CON mod (1) = 7
        class_levels = ClassLevels(
            base_class=CharacterClass.WIZARD,
            level_per_class={CharacterClass.WIZARD: 1},
        )
        hit_points = HitPoints().calculate(
            class_levels,
            standard_abilities.get_modifier(Ability.CONSTITUTION),
            None,
        )
        assert hit_points == 7  # 6 + 1

    def test_calculate_hit_points_multi_level(self, standard_abilities):
        """Test hit point calculation for multi-level character."""
        # Fighter level 5: 10 (d10) + 1 (CON) + (4 * (6 avg + 1 CON)) = 11 + 28 = 39
        class_levels = ClassLevels(
            base_class=CharacterClass.FIGHTER,
            level_per_class={CharacterClass.FIGHTER: 5},
        )
        hit_points = HitPoints().calculate(
            class_levels,
            standard_abilities.get_modifier(Ability.CONSTITUTION),
            None,
        )
        # 11 (level 1) + 4*(7 (average d10 + CON mod))
        assert hit_points == 11 + 4 * 7

    def test_calculate_hit_points_with_bonus(self):
        """Test that hit point bonuses are applied."""
        hit_points_part = HitPoints()
        hit_points_part.add_bonus(5)
        class_levels = ClassLevels(
            base_class=CharacterClass.WIZARD,
            level_per_class={CharacterClass.WIZARD: 1},
        )
        hit_points = hit_points_part.calculate(class_levels, 0, None)
        assert hit_points == 6 + 5  # d6 + bonus


class TestRollConditions:
    def test_advantage_and_disadvantage_cancel(self, basic_skills):
        basic_skills.set_roll_condition(
            Skill.STEALTH, DiceRollCondition.ADVANTAGE, "Source A"
        )
        basic_skills.set_roll_condition(
            Skill.STEALTH, DiceRollCondition.DISADVANTAGE, "Heavy armor"
        )
        assert basic_skills.get_roll_condition(Skill.STEALTH) == (
            DiceRollCondition.NEUTRAL
        )
