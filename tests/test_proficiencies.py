"""Weapon, armor and tool proficiencies are granted by features.

The starting class grants its Core Traits proficiencies (ClassProficiencies),
a class gained by multiclassing grants its "As a Multiclass Character" subset
(MulticlassProficiencies), and every subclass/feat grant lives in the feature
that describes it. Expected values come from SourceTexts/ClassTexts/<class>.txt
and the features' own text.
"""

import pathlib
import re

import pytest

from CharacterContent.Classes.BaseClasses.ClassBuilder import (
    AppliedLevelFeatures,
    BaseClassLevelFeatures,
    MulticlassBuilder,
)
from CharacterContent.Features.CharacterFeats import GeneralFeats
from CharacterContent.Features.ClassFeatures.ClassProficiencies import (
    ClassProficiencies,
    MulticlassProficiencies,
)
from CharacterContent.Features.ClassFeatures.Druid import DruidFeatures
from CharacterContent.Features.SubClassFeatures2014.Cleric import ClericForgeFeatures
from CharacterContent.Items import Weapons
from CharacterContent.Items.Weapons import WeaponProficiency
from CharacterContent.ToolProficiencies import Proficiencies as Tools
from Core.Definitions import Ability, ArmorType, CharacterClass
from RunCharacterCreator import BuildSelector, ExampleSelector

ALL_BUILDS = {**BuildSelector.builds(), **ExampleSelector.builds()}

LIGHT, MEDIUM, SHIELD = ArmorType.LIGHT, ArmorType.MEDIUM, ArmorType.SHIELD
MARTIAL = WeaponProficiency.MARTIAL

# "As a Multiclass Character" in each SourceTexts/ClassTexts/<class>.txt
# (skill and Musical Instrument choices aren't modelled).
MULTICLASS_TEXT = {
    CharacterClass.ARTIFICER: ({LIGHT, MEDIUM, SHIELD}, set(), {"Tinker's Tools"}),
    CharacterClass.BARBARIAN: ({SHIELD}, {MARTIAL}, set()),
    CharacterClass.BARD: ({LIGHT}, set(), set()),
    CharacterClass.CLERIC: ({LIGHT, MEDIUM, SHIELD}, set(), set()),
    CharacterClass.DRUID: ({LIGHT, SHIELD}, set(), set()),
    CharacterClass.FIGHTER: ({LIGHT, MEDIUM, SHIELD}, {MARTIAL}, set()),
    CharacterClass.MONK: (set(), set(), set()),
    CharacterClass.PALADIN: ({LIGHT, MEDIUM, SHIELD}, {MARTIAL}, set()),
    CharacterClass.RANGER: ({LIGHT, MEDIUM, SHIELD}, {MARTIAL}, set()),
    CharacterClass.ROGUE: ({LIGHT}, set(), {"Thieves' Tools"}),
    CharacterClass.SORCERER: (set(), set(), set()),
    CharacterClass.WARLOCK: ({LIGHT}, set(), set()),
    CharacterClass.WIZARD: (set(), set(), set()),
}


@pytest.mark.parametrize("character_class", list(CharacterClass))
def test_multiclass_proficiencies_match_class_text(character_class, make_character):
    armor, weapons, tools = MULTICLASS_TEXT[character_class]
    character = make_character()
    MulticlassProficiencies(character_class).apply(character)
    assert character.armor_training == armor
    assert character.weapon_proficiencies == weapons
    assert {t.name for t in character.tool_proficiencies} == tools


def _multiclass_builder(character_class, level):
    return MulticlassBuilder(
        base_class=character_class,
        base_class_level_features=BaseClassLevelFeatures(
            base_class_features_by_level={}, subclass_features_by_level={}
        ),
        base_class_level=level,
        subclass="Test",
    )


class TestMulticlassing:
    def test_a_later_class_grants_its_multiclass_proficiencies(self):
        # Regression: multiclass builders granted no proficiencies at all, so
        # a Wizard 3 / Warlock 3 never got the Warlock's Light armor training.
        data = type(ALL_BUILDS["SpellSlotTestWizard3Warlock3"])().build()
        assert LIGHT in data.setup_character_stat_block().armor_training

    def test_resuming_a_class_does_not_grant_its_proficiencies_again(self):
        applied = AppliedLevelFeatures()
        data = _multiclass_builder(CharacterClass.WARLOCK, 1).create(None, applied)
        data = _multiclass_builder(CharacterClass.WARLOCK, 3).create(data, applied)
        bundles = [f for f in data.features if isinstance(f, ClassProficiencies)]
        assert [type(f) for f in bundles] == [MulticlassProficiencies]

    def test_starting_class_keeps_its_full_proficiencies(self):
        # Fighter 1 / Warlock 5: the Fighter's Heavy armor comes from its full
        # Core Traits, not the (Heavy-less) multiclass subset.
        data = type(ALL_BUILDS["Y2024_Warlock_Archfey_CaelumBladefey"])().build()
        character = data.setup_character_stat_block()
        assert ArmorType.HEAVY in character.armor_training
        assert MARTIAL in character.weapon_proficiencies


class TestFeaturesGrantProficiencies:
    def test_martial_weapon_training_feat(self, make_character):
        # "Weapon Proficiency. You gain proficiency with Martial weapons."
        character = make_character(strength=14)
        longsword = Weapons.Longsword()
        assert not longsword.is_proficient(character)
        GeneralFeats.MartialWeaponTraining(
            character_level=4, ability=Ability.STRENGTH
        ).apply(character)
        assert longsword.is_proficient(character)
        assert character.get_ability_score(Ability.STRENGTH) == 15

    def test_druid_warden(self, make_character):
        # "Warden. Trained for battle, you gain proficiency with Martial
        # weapons and training with Medium armor." (only Medium armor used to
        # be granted)
        character = make_character()
        DruidFeatures.PrimalOrder(DruidFeatures.PrimalOrderType.WARDEN).apply(
            character
        )
        assert MARTIAL in character.weapon_proficiencies
        assert MEDIUM in character.armor_training

    def test_druid_magician_grants_no_proficiencies(self, make_character):
        character = make_character()
        DruidFeatures.PrimalOrder(DruidFeatures.PrimalOrderType.MAGICIAN).apply(
            character
        )
        assert not character.weapon_proficiencies
        assert not character.armor_training

    def test_forge_domain_smiths_tools(self, make_character):
        # "You gain proficiency with heavy armor and smith's tools."
        character = make_character()
        ClericForgeFeatures.BonusProficiencies().apply(character)
        assert ArmorType.HEAVY in character.armor_training
        assert [t.name for t in character.tool_proficiencies] == [
            Tools.SmithsTools().name
        ]


def test_builders_grant_proficiencies_only_through_features():
    # A proficiency granted on the sheet data directly bypasses the feature
    # that describes it (and its text) - grant it in that feature's apply().
    root = pathlib.Path(__file__).resolve().parent.parent / "CharacterContent"
    offenders = [
        f"{path.relative_to(root.parent)}:{number}"
        for path in root.rglob("*.py")
        for number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        )
        if re.search(r"\bdata\.add_(weapon|armor|tool)_proficiency\(", line)
    ]
    assert not offenders, "\n".join(offenders)
