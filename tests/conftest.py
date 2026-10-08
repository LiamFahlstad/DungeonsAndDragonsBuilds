"""
Shared pytest fixtures and configuration for D&D character sheet builder tests.
"""

import pytest
from Core.Definitions import Ability
from Model.AbilityScores import StandardArrayAbilityScores
from Model.ArmorClass import ArmorClass
from Model.CarryingCapacity import CarryingCapacity
from Model.Skills import Skills
from Model.SavingThrows import SavingThrows


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
def make_sources():
    """Factory for the CharacterSources of a bare character (no features).
    Grant it something, then build the character:

        sources = make_sources(dexterity=16, levels={CharacterClass.FIGHTER: 5})
        sources.add_effect(SomeFeature())
        character = Character(sources)

    make_sources(armor_training=[ArmorType.SHIELD]) adds that training.
    """
    from Model.Content.Improvements import GrantArmorTraining
    from Core.Definitions import CharacterClass, CreatureSize
    from Model.AbilityScores import AbilityScores
    from Model.CharacterSources import CharacterSources
    from Model.ClassLevels import ClassLevels

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
        sources = CharacterSources(
            character_name="Test Character",
            class_levels=ClassLevels(
                base_class=next(iter(levels)),
                level_per_class=levels,
                character_subclass="Test Subclass",
            ),
            base_abilities=AbilityScores(
                strength, dexterity, constitution, intelligence, wisdom, charisma
            ),
            base_speed=30,
            size=CreatureSize.MEDIUM,
        )
        # Armor training (ArmorType values) - untrained armor has penalties.
        if armor_training:
            sources.add_effect(GrantArmorTraining(list(armor_training)))
        return sources

    return _make


@pytest.fixture
def make_character(make_sources):
    """Factory for a bare, finished Character: make_sources(...) built as is.
    To grant it something first, use make_sources."""
    from Model.Character import Character

    def _make(**kwargs):
        return Character(make_sources(**kwargs))

    return _make
