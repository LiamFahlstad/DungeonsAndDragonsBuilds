"""
Shared pytest fixtures and configuration for D&D character sheet builder tests.
"""

import pytest
from Core.Definitions import Ability
from StatBlocks.AbilityScores import StandardArrayAbilityScores
from StatBlocks.ArmorClass import ArmorClass
from StatBlocks.CarryingCapacity import CarryingCapacity
from StatBlocks.Skills import Skills
from StatBlocks.SavingThrows import SavingThrows


@pytest.fixture
def standard_abilities():
    """A standard array abilities stat block for testing."""
    return StandardArrayAbilityScores(
        strength=15,
        dexterity=14,
        constitution=13,
        intelligence=12,
        wisdom=10,
        charisma=8,
    )


@pytest.fixture
def basic_skills():
    """A basic skills stat block for testing."""
    return Skills()


@pytest.fixture
def basic_saving_throws():
    """A basic saving throws stat block for testing."""
    return SavingThrows()


@pytest.fixture
def basic_armor_class():
    """A basic ArmorClass part for testing."""
    return ArmorClass()


@pytest.fixture
def basic_carrying_capacity():
    """A basic CarryingCapacity part for testing."""
    return CarryingCapacity()


@pytest.fixture
def make_character():
    """Factory for a bare CharacterStatBlock (no features applied).

    make_character(dexterity=16, levels={CharacterClass.FIGHTER: 5})
    make_character(armor_training=[ArmorType.SHIELD])
    """
    from Core.Definitions import CharacterClass
    from StatBlocks.AbilityScores import AbilityScores
    from StatBlocks.CharacterStatBlock import CharacterStatBlock
    from StatBlocks.ClassLevels import ClassLevels
    from StatBlocks.Spellcasting import Spellcasting

    def _make(
        strength=10,
        dexterity=10,
        constitution=10,
        intelligence=10,
        wisdom=10,
        charisma=10,
        levels=None,
        armor_training=(),
    ):
        levels = levels or {CharacterClass.FIGHTER: 1}
        character = CharacterStatBlock(
            class_levels=ClassLevels(
                base_class=next(iter(levels)), level_per_class=levels
            ),
            abilities=AbilityScores(
                strength, dexterity, constitution, intelligence, wisdom, charisma
            ),
            speed=30,
            spellcasting=Spellcasting(fixed_slots={}),
        )
        # Armor training (ArmorType values) - untrained armor has penalties.
        character.equipment_training.armor_training.update(armor_training)
        return character

    return _make
