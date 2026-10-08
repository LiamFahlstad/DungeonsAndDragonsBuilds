"""Weapon, armor and tool proficiencies are granted by features.

The starting class grants its Core Traits proficiencies (ClassProficiencies),
a class gained by multiclassing grants its "As a Multiclass Character" subset
(MulticlassProficiencies), and every subclass/feat grant lives in the feature
that describes it. Expected values come from SourceTexts/ClassTexts/<class>.txt
and the features' own text.
"""

import itertools
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
from CharacterContent.Features.ClassFeatures.Monk import MonkFeatures
from Model.Content.Improvements import (
    GrantArmorTraining,
    InitiativeRollCondition,
    SavingThrowAdvantage,
    SkillToAbilityOverride,
)
from CharacterContent.Features.SubClassFeatures2014.Cleric import ClericForgeFeatures
from CharacterContent.Items import Armor, Weapons
from CharacterContent.Items.Weapons import WeaponProficiency
from CharacterContent.ToolProficiencies import Proficiencies as Tools
from Core.Definitions import (
    Ability,
    ArmorType,
    CharacterClass,
    DiceRollCondition,
    Skill,
)
from RunCharacterCreator import BuildSelector, ExampleSelector
from Presentation.CharacterSheetWriters import HtmlCharacterSheetWriter
from Model.Character import Character

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
def test_multiclass_proficiencies_match_class_text(character_class, make_sources):
    armor, weapons, tools = MULTICLASS_TEXT[character_class]
    sources = make_sources()
    sources.add_effect(MulticlassProficiencies(character_class))
    character = Character(sources)
    assert character.ledger.equipment_training.armor_training == armor
    assert character.ledger.equipment_training.weapon_proficiencies == weapons
    assert {
        t.name for t in character.ledger.equipment_training.tool_proficiencies
    } == tools


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
        assert LIGHT in data.validate().ledger.equipment_training.armor_training

    def test_resuming_a_class_does_not_grant_its_proficiencies_again(self):
        applied = AppliedLevelFeatures()
        sources = _multiclass_builder(CharacterClass.WARLOCK, 1).create(None, applied)
        sources = _multiclass_builder(CharacterClass.WARLOCK, 3).create(
            sources, applied
        )
        features = Character(sources).features
        bundles = [f for f in features if isinstance(f, ClassProficiencies)]
        assert [type(f) for f in bundles] == [MulticlassProficiencies]

    def test_starting_class_keeps_its_full_proficiencies(self):
        # Fighter 1 / Warlock 5: the Fighter's Heavy armor comes from its full
        # Core Traits, not the (Heavy-less) multiclass subset.
        data = type(ALL_BUILDS["Y2024_Warlock_Archfey_CaelumBladefey"])().build()
        character = data.validate()
        assert ArmorType.HEAVY in character.ledger.equipment_training.armor_training
        assert MARTIAL in character.ledger.equipment_training.weapon_proficiencies


class TestFeaturesGrantProficiencies:
    def test_martial_weapon_training_feat(self, make_sources):
        # "Weapon Proficiency. You gain proficiency with Martial weapons."
        sources = make_sources(strength=14)
        longsword = Weapons.Longsword()
        character = Character(sources)
        assert not longsword.is_proficient(character)
        sources.add_effect(
            GeneralFeats.MartialWeaponTraining(
                character_level=4, ability=Ability.STRENGTH
            )
        )
        character = Character(sources)
        assert longsword.is_proficient(character)
        assert character.get_ability_score(Ability.STRENGTH) == 15

    def test_druid_warden(self, make_sources):
        # "Warden. Trained for battle, you gain proficiency with Martial
        # weapons and training with Medium armor." (only Medium armor used to
        # be granted)
        sources = make_sources()
        sources.add_effect(
            DruidFeatures.PrimalOrder(DruidFeatures.PrimalOrderType.WARDEN)
        )
        character = Character(sources)
        assert MARTIAL in character.ledger.equipment_training.weapon_proficiencies
        assert MEDIUM in character.ledger.equipment_training.armor_training

    def test_druid_magician_grants_no_proficiencies(self, make_sources):
        sources = make_sources()
        sources.add_effect(
            DruidFeatures.PrimalOrder(DruidFeatures.PrimalOrderType.MAGICIAN)
        )
        character = Character(sources)
        assert not character.ledger.equipment_training.weapon_proficiencies
        assert not character.ledger.equipment_training.armor_training

    def test_forge_domain_smiths_tools(self, make_sources):
        # "You gain proficiency with heavy armor and smith's tools."
        sources = make_sources()
        sources.add_effect(ClericForgeFeatures.BonusProficiencies())
        character = Character(sources)
        assert ArmorType.HEAVY in character.ledger.equipment_training.armor_training
        assert [
            t.name for t in character.ledger.equipment_training.tool_proficiencies
        ] == [Tools.SmithsTools().name]


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


# ── Armor training (2024 PHB) ─────────────────────────────────────────────────
# "If you wear armor and lack training with it, you have Disadvantage on any
# D20 Test that involves Strength or Dexterity, and you can't cast spells. If
# you use a Shield and lack training with it, you don't gain its AC bonus."

DIS, ADV, NEUTRAL = (
    DiceRollCondition.DISADVANTAGE,
    DiceRollCondition.ADVANTAGE,
    DiceRollCondition.NEUTRAL,
)


class TestArmorTraining:
    def test_untrained_shield_grants_no_ac(self, make_sources):
        untrained_sources = make_sources(dexterity=14)
        untrained_sources.add_effect(Armor.ShieldArmor())
        untrained = Character(untrained_sources)
        assert untrained.calculate_armor_class() == 12
        assert untrained.warnings == [
            "Wielding a Shield without Shield training: it grants no AC bonus."
        ]
        trained_sources = make_sources(dexterity=14, armor_training=[SHIELD])
        trained_sources.add_effect(Armor.ShieldArmor())
        trained = Character(trained_sources)
        assert trained.calculate_armor_class() == 14
        assert trained.warnings == []

    def test_untrained_armor_disadvantage_on_strength_and_dexterity(self, make_sources):
        sources = make_sources(dexterity=14)
        sources.add_effect(Armor.LeatherArmor())
        # AC itself is unaffected.
        character = Character(sources)
        assert character.calculate_armor_class() == 11 + 2
        for skill in (Skill.ATHLETICS, Skill.ACROBATICS, Skill.STEALTH):
            assert character.get_skill_roll_condition(skill) == DIS
            assert character.get_skill_roll_condition_reasons(skill) == [
                "Untrained armor"
            ]
        assert character.get_skill_roll_condition(Skill.ARCANA) == NEUTRAL
        for ability in (Ability.STRENGTH, Ability.DEXTERITY):
            assert character.get_saving_throw_roll_condition(ability) == DIS
        assert character.get_saving_throw_roll_condition(Ability.WISDOM) == NEUTRAL
        assert character.initiative_roll_condition == DIS
        assert Weapons.Longsword().attack_roll_condition(character) == DIS
        assert Weapons.Longbow().attack_roll_condition(character) == DIS
        assert (
            Weapons.Longsword(ability=Ability.INTELLIGENCE).attack_roll_condition(
                character
            )
            == NEUTRAL
        )
        assert character.warnings == [
            "Wearing Leather Armor without Light armor training: Disadvantage on "
            "every D20 Test that involves Strength or Dexterity, and you can't "
            "cast spells."
        ]

    def test_skill_uses_its_actual_ability(self, make_sources):
        # Athletics rolled with Wisdom isn't a Strength test.
        sources = make_sources(wisdom=14)
        sources.add_effect(SkillToAbilityOverride([Skill.ATHLETICS], Ability.WISDOM))
        sources.add_effect(Armor.LeatherArmor())
        character = Character(sources)
        assert character.get_skill_roll_condition(Skill.ATHLETICS) == NEUTRAL

    def test_cancels_with_advantage(self, make_sources):
        sources = make_sources()
        sources.add_effect(Armor.LeatherArmor())
        sources.add_effect(InitiativeRollCondition(ADV))
        sources.add_effect(SavingThrowAdvantage([Ability.DEXTERITY]))
        character = Character(sources)
        assert character.initiative_roll_condition == NEUTRAL
        assert character.get_saving_throw_roll_condition(Ability.DEXTERITY) == NEUTRAL

    def test_training_granted_after_the_armor_counts(self, make_sources):
        effects = [
            Armor.LeatherArmor(),
            Armor.ShieldArmor(),
            GrantArmorTraining([LIGHT, SHIELD]),
        ]
        for ordered in itertools.permutations(effects):
            sources = make_sources(dexterity=14)
            for effect in ordered:
                sources.add_effect(effect)
            character = Character(sources)
            assert character.warnings == []
            assert character.get_skill_roll_condition(Skill.STEALTH) == NEUTRAL
            assert character.calculate_armor_class() == 11 + 2 + 2

    def test_armor_class_without_the_shield(self, make_sources):
        # A Monk's Unarmored Defense stops working with a Shield; setting the
        # Shield aside brings it back (the sheet's "w/o Shield" figure).
        sources = make_sources(dexterity=14, wisdom=16, armor_training=[SHIELD])
        sources.add_effect(MonkFeatures.UnarmoredDefense())
        sources.add_effect(Armor.ShieldArmor())
        character = Character(sources)
        assert character.calculate_armor_class() == 10 + 2 + 2
        assert character.calculate_armor_class(ignore_shield=True) == 10 + 2 + 3

    def test_sheet_shows_the_warning(self, tmp_path):
        sources = type(ALL_BUILDS["SpellSlotTestWizard5"])().build().sources
        sources.add_armor(Armor.LeatherArmor())  # without armor training
        HtmlCharacterSheetWriter().write_character_sheet(
            Character(sources), output_folder=str(tmp_path)
        )
        page = (tmp_path / "character.html").read_text(encoding="utf-8")
        assert "class='sheet-warning'" in page
        assert "without Light armor training" in page
