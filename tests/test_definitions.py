"""
Tests for Core/Definitions.py - enums and constants for D&D mechanics.
"""

import pytest
from Core.Definitions import (
    Ability,
    Skill,
    CharacterClass,
    Species,
    SkillConfig,
    HomeBrewSkill,
    MAX_PROFICIENCY_BONUS,
    MAX_ABILITY_MODIFIER,
)


class TestAbilityEnum:
    """Test Ability enum properties."""

    def test_ability_values(self):
        """Test that Ability enum has correct values."""
        assert Ability.STRENGTH.value == "Strength"
        assert Ability.DEXTERITY.value == "Dexterity"
        assert Ability.CONSTITUTION.value == "Constitution"
        assert Ability.INTELLIGENCE.value == "Intelligence"
        assert Ability.WISDOM.value == "Wisdom"
        assert Ability.CHARISMA.value == "Charisma"

    def test_ability_short_names(self):
        """Test that short_name property returns correct abbreviations."""
        assert Ability.STRENGTH.short_name == "STR"
        assert Ability.DEXTERITY.short_name == "DEX"
        assert Ability.CONSTITUTION.short_name == "CON"
        assert Ability.INTELLIGENCE.short_name == "INT"
        assert Ability.WISDOM.short_name == "WIS"
        assert Ability.CHARISMA.short_name == "CHA"

    def test_all_abilities_have_short_names(self):
        """Test that every ability has a short_name."""
        for ability in Ability:
            assert hasattr(ability, "short_name")
            assert len(ability.short_name) == 3


class TestSkillEnum:
    """Test Skill enum properties and sorting."""

    def test_skill_values(self):
        """Test that Skill enum has correct values."""
        assert Skill.ACROBATICS.value == "Acrobatics"
        assert Skill.ANIMAL_HANDLING.value == "Animal Handling"
        assert Skill.ARCANA.value == "Arcana"
        assert Skill.STEALTH.value == "Stealth"
        assert len(Skill) == 18  # D&D 5e has 18 skills

    def test_skill_list_sorted(self):
        """Test that Skill.list_sorted() returns alphabetically sorted skills."""
        sorted_skills = Skill.list_sorted()
        assert len(sorted_skills) == len(Skill)
        # Check that it's actually sorted
        sorted_values = [s.value for s in sorted_skills]
        assert sorted_values == sorted(sorted_values)

    def test_unique_skills(self):
        """Test that all skills are unique."""
        assert len(Skill) == len(set(Skill))


class TestHomeBrewSkillEnum:
    """Test HomeBrewSkill enum and conversion to default skills."""

    def test_homebrew_skill_values(self):
        """Test that HomeBrewSkill enum has expected values."""
        assert HomeBrewSkill.ACROBATICS.value == "Acrobatics"
        assert HomeBrewSkill.SPIRIT.value == "Spirit"
        assert HomeBrewSkill.ARCANA.value == "Arcana"

    def test_homebrew_skill_list_sorted(self):
        """Test that HomeBrewSkill.list_sorted() returns alphabetically sorted."""
        sorted_skills = HomeBrewSkill.list_sorted()
        sorted_values = [s.value for s in sorted_skills]
        assert sorted_values == sorted(sorted_values)

    def test_map_homebrew_to_default_spirit(self):
        """Test that SPIRIT homebrew skill maps to ANIMAL_HANDLING."""
        default_skills = SkillConfig.map_homebrew_to_default(HomeBrewSkill.SPIRIT)
        assert Skill.ANIMAL_HANDLING in default_skills

    def test_map_homebrew_to_default_lore(self):
        """Test that LORE homebrew skill maps to HISTORY and RELIGION."""
        default_skills = SkillConfig.map_homebrew_to_default(HomeBrewSkill.LORE)
        assert Skill.HISTORY in default_skills
        assert Skill.RELIGION in default_skills
        assert len(default_skills) == 2

    def test_map_homebrew_to_default_nature(self):
        """Test that NATURE homebrew skill maps to NATURE and SURVIVAL."""
        default_skills = SkillConfig.map_homebrew_to_default(HomeBrewSkill.NATURE)
        assert Skill.NATURE in default_skills
        assert Skill.SURVIVAL in default_skills
        assert len(default_skills) == 2

    def test_all_homebrew_skills_have_mappings(self):
        """Test that all homebrew skills have default skill mappings."""
        for homebrew_skill in HomeBrewSkill:
            default_skills = SkillConfig.map_homebrew_to_default(homebrew_skill)
            assert len(default_skills) > 0


class TestCharacterClassEnum:
    """Test CharacterClass enum and hit die properties."""

    def test_character_class_values(self):
        """Test that CharacterClass enum has correct values."""
        assert CharacterClass.FIGHTER.value == "Fighter"
        assert CharacterClass.WIZARD.value == "Wizard"
        assert CharacterClass.BARBARIAN.value == "Barbarian"
        assert len(CharacterClass) == 13  # D&D 5e has 13 classes

    def test_hit_die_property(self):
        """Test that each class returns correct hit die size."""
        expected_hit_dice = {
            CharacterClass.ARTIFICER: 8,
            CharacterClass.BARBARIAN: 12,
            CharacterClass.BARD: 8,
            CharacterClass.CLERIC: 8,
            CharacterClass.DRUID: 8,
            CharacterClass.FIGHTER: 10,
            CharacterClass.MONK: 8,
            CharacterClass.PALADIN: 10,
            CharacterClass.RANGER: 10,
            CharacterClass.ROGUE: 8,
            CharacterClass.SORCERER: 6,
            CharacterClass.WARLOCK: 8,
            CharacterClass.WIZARD: 6,
        }
        for character_class, expected_die in expected_hit_dice.items():
            assert character_class.hit_die == expected_die

    def test_average_hit_die_property(self):
        """Test that average_hit_die returns (die // 2) + 1."""
        # For d6: (6 // 2) + 1 = 4
        assert CharacterClass.WIZARD.average_hit_die == 4
        # For d8: (8 // 2) + 1 = 5
        assert CharacterClass.BARD.average_hit_die == 5
        # For d10: (10 // 2) + 1 = 6
        assert CharacterClass.FIGHTER.average_hit_die == 6
        # For d12: (12 // 2) + 1 = 7
        assert CharacterClass.BARBARIAN.average_hit_die == 7


class TestSpeciesEnum:
    """Test Species enum values."""

    def test_species_values(self):
        """Test that Species enum has correct values."""
        assert Species.HUMAN.value == "Human"
        assert Species.ELF.value == "Elf"
        assert Species.DWARF.value == "Dwarf"
        assert Species.HALFLING.value == "Halfling"
        assert len(Species) == 8  # D&D 5e has 8 core species

    def test_all_species_have_values(self):
        """Test that all species are defined."""
        species_list = list(Species)
        assert Species.HUMAN in species_list
        assert Species.ORC in species_list


class TestSkillConfig:
    """Test SkillConfig enum."""

    def test_skill_config_values(self):
        """Test that SkillConfig enum has correct values."""
        assert SkillConfig.DEFAULT.value == "Default"
        assert SkillConfig.HOMEBREW.value == "Homebrew"


class TestConstants:
    """Test module-level constants."""

    def test_max_proficiency_bonus(self):
        """Test that MAX_PROFICIENCY_BONUS is 6 (max at level 20)."""
        assert MAX_PROFICIENCY_BONUS == 6

    def test_max_ability_modifier(self):
        """Test that MAX_ABILITY_MODIFIER is 10 (score of 30)."""
        assert MAX_ABILITY_MODIFIER == 10
