"""Example build: Monk Warrior of Mercy. Adapted from an optimized reference build to demonstrate this subclass."""

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
from CharacterConfigs.SubClasses2024.MonkMercy import (
    MonkMercyCustomStarterClassArgs,
    MonkMercyLevel3,
    MonkMercyLevel6,
    MonkMercyLevel11,
    MonkMercyLevel17,
)
from Core.Definitions import Ability, Skill
from Features.CharacterFeats import Backgrounds, GeneralFeats, OriginFeats
from SpeciesConfigs import Elf
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import MonkSkillsStatBlock


def get_starter_class_builder():
    monk_level = 17
    return StarterClassBuilder(
        non_generic_arguments=MonkMercyCustomStarterClassArgs(
            skills=MonkSkillsStatBlock(
                proficiencies={
                    Skill.ACROBATICS: True,
                    Skill.ATHLETICS: False,
                    Skill.HISTORY: False,
                    Skill.INSIGHT: True,
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
                Skill.MEDICINE,
                Skill.INSIGHT,
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
                        [
                            (Ability.WISDOM, 2),
                        ]
                    ),
                ),
                5: MonkLevel5(),
                6: MonkLevel6(),
                7: MonkLevel7(),
                8: MonkLevel8(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.DEXTERITY, 2),
                        ]
                    ),
                ),
                9: MonkLevel9(),
                10: MonkLevel10(),
                11: MonkLevel11(),
                12: MonkLevel12(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.WISDOM, 2),
                        ]
                    ),
                ),
                13: MonkLevel13(),
                14: MonkLevel14(),
                15: MonkLevel15(),
                16: MonkLevel16(
                    general_feat=GeneralFeats.AbilityScoreImprovement(
                        [
                            (Ability.CONSTITUTION, 2),
                        ]
                    ),
                ),
                17: MonkLevel17(),
            },
            subclass_features_by_level={
                3: MonkMercyLevel3(),
                6: MonkMercyLevel6(),
                11: MonkMercyLevel11(),
                17: MonkMercyLevel17(),
            },
        ),
    )


class ExampleMonkMercyCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Example Mercy Monk",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Elf.ElfSpeciesBuilder(
                elven_lineage=Elf.ElvenLineage.WOOD_ELF,
                skill_proficiency=Definitions.Skill.PERCEPTION,
            ),
        )
