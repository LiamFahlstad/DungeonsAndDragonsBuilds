"""Example build: Wizard School of Graviturgy (2014 rules). Demonstrates the subclass through level 14."""

import Core.Definitions as Definitions
from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.BaseClasses.WizardBase import (
    WizardLevel1,
    WizardLevel2,
    WizardLevel3,
    WizardLevel4,
    WizardLevel5,
    WizardLevel6,
    WizardLevel7,
    WizardLevel8,
    WizardLevel9,
    WizardLevel10,
    WizardLevel11,
    WizardLevel12,
    WizardLevel13,
    WizardLevel14,
)
from CharacterContent.Classes.SubClasses2014.WizardGraviturgy import (
    WizardGraviturgyLevel3,
    WizardGraviturgyLevel6,
    WizardGraviturgyLevel10,
    WizardGraviturgyLevel14,
    WizardGraviturgyCustomStarterClassArgs,
)
from Core.Definitions import Ability, Skill
from CharacterContent.Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from CharacterContent.Species import Gnome
from CharacterContent.Spells import SpellLists as SpellDefinitions
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import WizardSkillsStatBlock


def get_starter_class_builder():
    return StarterClassBuilder(
        non_generic_arguments=WizardGraviturgyCustomStarterClassArgs(
            skills=WizardSkillsStatBlock(
                proficiencies={
                    Skill.ARCANA: True,
                    Skill.HISTORY: False,
                    Skill.INSIGHT: False,
                    Skill.INVESTIGATION: True,
                    Skill.MEDICINE: False,
                    Skill.NATURE: False,
                    Skill.RELIGION: False,
                }
            ),
        ),
        base_class_level=14,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=8,
            dexterity=14,
            constitution=13,
            intelligence=15,
            wisdom=10,
            charisma=12,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.INTELLIGENCE, 2),
                (Ability.CONSTITUTION, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.RELIGION,
                Skill.PERCEPTION,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Alert(),
        armor=[],
        weapons=[],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: WizardLevel1(
                    cantrip_1=SpellDefinitions.WizardLevel0Spells.FIRE_BOLT,
                    cantrip_2=SpellDefinitions.WizardLevel0Spells.MAGE_HAND,
                    cantrip_3=SpellDefinitions.WizardLevel0Spells.PRESTIDIGITATION,
                    spell_1=SpellDefinitions.WizardLevel1Spells.SHIELD,
                    spell_2=SpellDefinitions.WizardLevel1Spells.MAGE_ARMOR,
                    spell_3=SpellDefinitions.WizardLevel1Spells.ALARM,
                    spell_4=SpellDefinitions.WizardLevel1Spells.DETECT_MAGIC,
                ),
                2: WizardLevel2(
                    skill_expertise=Skill.ARCANA,
                    spell=SpellDefinitions.WizardLevel1Spells.FEATHER_FALL,
                ),
                3: WizardLevel3(
                    spell=SpellDefinitions.WizardLevel2Spells.LEVITATE,
                ),
                4: WizardLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.INTELLIGENCE, 2),
                        ]),
                    cantrip=SpellDefinitions.WizardLevel0Spells.RAY_OF_FROST,
                    spell=SpellDefinitions.WizardLevel2Spells.MAGIC_WEAPON,
                ),
                5: WizardLevel5(
                    spell_1=SpellDefinitions.WizardLevel3Spells.FLY,
                    spell_2=SpellDefinitions.WizardLevel3Spells.COUNTERSPELL,
                ),
                6: WizardLevel6(
                    spell=SpellDefinitions.WizardLevel3Spells.HASTE,
                ),
                7: WizardLevel7(
                    spell=SpellDefinitions.WizardLevel4Spells.BANISHMENT,
                ),
                8: WizardLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.INTELLIGENCE, 2),
                        ]),
                    spell=SpellDefinitions.WizardLevel4Spells.STONESKIN,
                ),
                9: WizardLevel9(
                    spell_1=SpellDefinitions.WizardLevel5Spells.WALL_OF_FORCE,
                    spell_2=SpellDefinitions.WizardLevel5Spells.TELEKINESIS,
                ),
                10: WizardLevel10(
                    cantrip=SpellDefinitions.WizardLevel0Spells.FROSTBITE,
                    spell=SpellDefinitions.WizardLevel5Spells.WALL_OF_STONE,
                ),
                11: WizardLevel11(
                    spell=SpellDefinitions.WizardLevel6Spells.GLOBE_OF_INVULNERABILITY,
                ),
                12: WizardLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[
                            (Ability.CONSTITUTION, 2),
                        ]),
                ),
                13: WizardLevel13(
                    spell=SpellDefinitions.WizardLevel7Spells.REVERSE_GRAVITY,
                ),
                14: WizardLevel14(
                    spell=SpellDefinitions.WizardLevel7Spells.SIMULACRUM,
                ),
            },
            subclass_features_by_level={
                3: WizardGraviturgyLevel3(),
                6: WizardGraviturgyLevel6(),
                10: WizardGraviturgyLevel10(),
                14: WizardGraviturgyLevel14(),
            },
        ),
        replace_spells={},
    )


class Y2014WizardGraviturgyOrbeckGravewellCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Orbeck Gravewell",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Gnome.RockGnomeSpeciesBuilder(),
        )
