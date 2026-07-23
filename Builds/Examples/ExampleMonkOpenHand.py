"""Example build: Monk Warrior of the Open Hand. Adapted from an optimized reference build to demonstrate this subclass."""

import Core.Definitions as Definitions
from Builds.CharacterBuilder import CharacterBuilder
from CharacterConfigs.BaseClasses import ClassBuilder
from CharacterConfigs.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterConfigs.BaseClasses.MonkBase import (
    MonkLevel1,
    MonkLevel2,
    MonkLevel3,
    MonkLevel4,
    MonkLevel5,
    MonkLevel6,
    MonkLevel7,
    MonkLevel8,
    MonkLevel9,
    MonkLevel10,
    MonkLevel11,
    MonkLevel12,
    MonkLevel13,
    MonkLevel14,
    MonkLevel15,
    MonkLevel16,
    MonkLevel17,
)
from CharacterConfigs.SubClasses2024.MonkOpenHand import (
    MonkOpenHandCustomStarterClassArgs,
    MonkOpenHandLevel3,
    MonkOpenHandLevel6,
    MonkOpenHandLevel11,
    MonkOpenHandLevel17,
)
from Core.Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from SpeciesConfigs import Elf
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import MonkSkillsStatBlock


def get_starter_class_builder():
    monk_level = 17
    return StarterClassBuilder(
        non_generic_arguments=MonkOpenHandCustomStarterClassArgs(
            skills=MonkSkillsStatBlock(
                proficiencies={
                    Skill.ACROBATICS: True,
                    Skill.ATHLETICS: True,
                    Skill.HISTORY: False,
                    Skill.INSIGHT: False,
                    Skill.RELIGION: False,
                    Skill.STEALTH: False,
                }
            ),
            monk_level=monk_level,
            unarmed_strike=Ability.DEXTERITY,
        ),
        base_class_level=monk_level,
        # Distribute 15, 14, 13, 12, 10, 8 among your abilities.
        abilities=StandardArrayAbilitiesStatBlock(
            strength=8,
            dexterity=15,
            constitution=13,
            intelligence=10,
            wisdom=14,
            charisma=12,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.WISDOM, 2),
                (Ability.DEXTERITY, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.SLEIGHT_OF_HAND,
                Skill.PERSUASION,
            ]
        ),
        add_default_equipment=True,
        origin_feat=OriginFeats.Alert(),
        armor=[],
        weapons=[],
        base_class_level_features=ClassBuilder.BaseClassLevelFeatures(
            base_class_features_by_level={
                1: MonkLevel1(),
                2: MonkLevel2(),
                3: MonkLevel3(),
                4: MonkLevel4(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.WISDOM, 2)]),
                ),
                5: MonkLevel5(),
                6: MonkLevel6(),
                7: MonkLevel7(),
                8: MonkLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.DEXTERITY, 2)]),
                ),
                9: MonkLevel9(),
                10: MonkLevel10(),
                11: MonkLevel11(),
                12: MonkLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.WISDOM, 2)]),
                ),
                13: MonkLevel13(),
                14: MonkLevel14(),
                15: MonkLevel15(),
                16: MonkLevel16(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        bonuses=[(Ability.DEXTERITY, 2)]),
                ),
                17: MonkLevel17(),
            },
            subclass_features_by_level={
                3: MonkOpenHandLevel3(),
                6: MonkOpenHandLevel6(),
                11: MonkOpenHandLevel11(),
                17: MonkOpenHandLevel17(),
            },
        ),
    )


class ExampleMonkOpenHandCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Open Hand Monk",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Elf.ElfSpeciesBuilder(
                elven_lineage=Elf.ElvenLineage.WOOD_ELF,
                skill_proficiency=Definitions.Skill.PERCEPTION,
            ),
        )
