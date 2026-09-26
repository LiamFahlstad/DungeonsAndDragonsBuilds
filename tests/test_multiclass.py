"""
Multiclassing rules (2024 PHB): ability prerequisites and how a multiclass
sheet names its subclasses.
"""

import pytest

from Builds.Tests.MulticlassTest import MulticlassTestCharacterBuilder
from Builds.Tests.SpellSlotTestPaladin4Wizard3 import (
    SpellSlotTestPaladin4Wizard3CharacterBuilder,
)
from Builds.Tests.SpellSlotTestWizard3Warlock3 import (
    SpellSlotTestWizard3Warlock3CharacterBuilder,
)
from Builds.Tests.SpellSlotTestWizard5 import SpellSlotTestWizard5CharacterBuilder
from Core.Definitions import Ability, CharacterClass

A = Ability

# 2024 PHB "Multiclassing" prerequisites, transcribed.
PHB_PREREQUISITES = {
    CharacterClass.BARBARIAN: [(A.STRENGTH,)],
    CharacterClass.BARD: [(A.CHARISMA,)],
    CharacterClass.CLERIC: [(A.WISDOM,)],
    CharacterClass.DRUID: [(A.WISDOM,)],
    CharacterClass.FIGHTER: [(A.STRENGTH, A.DEXTERITY)],
    CharacterClass.MONK: [(A.DEXTERITY,), (A.WISDOM,)],
    CharacterClass.PALADIN: [(A.STRENGTH,), (A.CHARISMA,)],
    CharacterClass.RANGER: [(A.DEXTERITY,), (A.WISDOM,)],
    CharacterClass.ROGUE: [(A.DEXTERITY,)],
    CharacterClass.SORCERER: [(A.CHARISMA,)],
    CharacterClass.WARLOCK: [(A.CHARISMA,)],
    CharacterClass.WIZARD: [(A.INTELLIGENCE,)],
}


@pytest.mark.parametrize("character_class", PHB_PREREQUISITES, ids=lambda c: c.name)
def test_prerequisite_table(character_class):
    expected = {frozenset(group) for group in PHB_PREREQUISITES[character_class]}
    actual = {frozenset(g) for g in character_class.multiclass_prerequisites}
    assert actual == expected


class TestPrerequisiteEnforced:
    def test_valid_multiclass_builds(self):
        data = SpellSlotTestWizard3Warlock3CharacterBuilder().build()
        data.setup_character_stat_block()

    def test_low_charisma_warlock_rejected(self):
        data = SpellSlotTestWizard3Warlock3CharacterBuilder().build()
        data.abilities.charisma = 10  # raw score; background +1 -> 11
        with pytest.raises(ValueError, match="Warlock requires Charisma 13"):
            data.setup_character_stat_block()

    def test_starting_class_also_checked(self):
        # Paladin 4 / Wizard 3 needs Paladin's STR 13 too.
        data = SpellSlotTestPaladin4Wizard3CharacterBuilder().build()
        data.abilities.strength = 8
        with pytest.raises(ValueError, match="Paladin requires Strength 13"):
            data.setup_character_stat_block()

    def test_single_class_not_checked(self):
        data = SpellSlotTestWizard5CharacterBuilder().build()
        data.abilities.intelligence = 8
        data.setup_character_stat_block()


class TestSubclassName:
    def test_both_subclasses_shown(self):
        data = SpellSlotTestPaladin4Wizard3CharacterBuilder().build()
        assert data.character_subclass == "Oath of Glory / Bladesinger"

    def test_class_below_subclass_level_omitted(self):
        # Fighter 1 hasn't chosen a subclass yet.
        data = MulticlassTestCharacterBuilder().build()
        assert data.character_subclass == "Bladesinger"

    def test_output_folder_has_no_slash(self):
        data = SpellSlotTestPaladin4Wizard3CharacterBuilder().build()
        assert "/" not in data.get_output_folder().removeprefix("Output/")
