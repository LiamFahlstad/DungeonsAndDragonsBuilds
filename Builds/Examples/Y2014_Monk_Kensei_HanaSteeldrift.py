"""Example build: Monk Way of the Kensei (2014 edition). Demonstrates this classic sword-and-technique subclass."""

import Core.Definitions as Definitions
from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.BaseClasses.MonkBase import MonkLevel1, MonkLevel2, MonkLevel3
from CharacterContent.Classes.SubClasses2014.MonkKensei import (
    MonkKenseiCustomStarterClassArgs,
    MonkKenseiLevel3,
    MonkKenseiLevel6,
    MonkKenseiLevel11,
    MonkKenseiLevel17,
)
from Core.Definitions import Ability, Skill
from CharacterContent.Features.CharacterFeats import Backgrounds, OriginFeats
from CharacterContent.Species import Human
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import MonkSkillsStatBlock
from CharacterContent.ToolProficiencies.Proficiencies import CalligraphersSupplies


def get_starter_class_builder():
    monk_level = 17
    return StarterClassBuilder(
        non_generic_arguments=MonkKenseiCustomStarterClassArgs(
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
            strength=10,
            dexterity=15,
            constitution=13,
            intelligence=12,
            wisdom=14,
            charisma=8,
        ),
        background_ability_bonuses=Backgrounds.FreeBackgroundAbilityBonus(
            [
                (Ability.WISDOM, 2),
                (Ability.DEXTERITY, 1),
            ]
        ),
        background_skill_proficiencies=Backgrounds.FreeBackgroundSkillProficiency(
            [
                Skill.INSIGHT,
                Skill.PERCEPTION,
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
            },
            subclass_features_by_level={
                3: MonkKenseiLevel3(),
                6: MonkKenseiLevel6(),
                11: MonkKenseiLevel11(),
                17: MonkKenseiLevel17(),
            },
        ),
        tool_proficiencies=[CalligraphersSupplies()],
    )


class Y2014MonkKenseiHanaSteeldriftCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Hana Steeldrift",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                origin_feat=OriginFeats.Alert(),
                skill_proficiency=Skill.PERCEPTION,
            ),
        )
