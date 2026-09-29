"""
Shared pytest fixtures and configuration for D&D character sheet builder tests.
"""

import pytest
from Core.Definitions import Ability
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import SkillsStatBlock
from StatBlocks.SavingThrowsStatBlock import SavingThrowsStatBlock
from StatBlocks.CombatStatBlock import CombatStatBlock
from Core.Definitions import CreatureSize


@pytest.fixture
def standard_abilities():
    """A standard array abilities stat block for testing."""
    return StandardArrayAbilitiesStatBlock(
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
    return SkillsStatBlock()


@pytest.fixture
def basic_saving_throws():
    """A basic saving throws stat block for testing."""
    return SavingThrowsStatBlock()


@pytest.fixture
def basic_combat():
    """A basic combat stat block for testing."""
    return CombatStatBlock(speed=30, size=CreatureSize.MEDIUM)


@pytest.fixture
def make_character():
    """Factory for a bare CharacterStatBlock (no features applied).

    make_character(dexterity=16, levels={CharacterClass.FIGHTER: 5})
    make_character(armor_training=[ArmorType.SHIELD])
    """
    from Core.Definitions import CharacterClass
    from StatBlocks.AbilitiesStatBlock import AbilitiesStatBlock
    from StatBlocks.CharacterStatBlock import CharacterStatBlock
    from StatBlocks.ClassLevels import ClassLevels

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
            abilities=AbilitiesStatBlock(
                strength, dexterity, constitution, intelligence, wisdom, charisma
            ),
            skills=SkillsStatBlock(),
            combat=CombatStatBlock(speed=30, size=CreatureSize.MEDIUM),
            saving_throws=SavingThrowsStatBlock(),
            spell_slots={},
        )
        # Armor training (ArmorType values) - untrained armor has penalties.
        character.armor_training.update(armor_training)
        return character

    return _make
