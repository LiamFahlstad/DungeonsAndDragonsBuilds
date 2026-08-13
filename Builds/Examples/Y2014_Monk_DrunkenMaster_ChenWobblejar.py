"""Example build: Monk Way of the Drunken Master (2014 edition). Demonstrates this unpredictable, mobile subclass."""

import Core.Definitions as Definitions
from Builds.CharacterBuilder import CharacterBuilder
from CharacterContent.Classes.BaseClasses import ClassBuilder
from CharacterContent.Classes.BaseClasses.ClassBuilder import StarterClassBuilder
from CharacterContent.Classes.BaseClasses.MonkBase import MonkLevel1, MonkLevel2, MonkLevel3
from CharacterContent.Classes.SubClasses2014.MonkDrunkenMaster import (
    MonkDrunkenMasterCustomStarterClassArgs,
    MonkDrunkenMasterLevel3,
    MonkDrunkenMasterLevel6,
    MonkDrunkenMasterLevel11,
    MonkDrunkenMasterLevel17,
)
from Core.Definitions import Ability, Skill
from CharacterContent.Features.CharacterFeats import Backgrounds, OriginFeats
from CharacterContent.Species import Human
from StatBlocks.AbilitiesStatBlock import StandardArrayAbilitiesStatBlock
from StatBlocks.SkillsStatBlock import MonkSkillsStatBlock
from CharacterContent.ToolProficiencies.Proficiencies import BrewersSupplies


def get_starter_class_builder():
    monk_level = 17
    return StarterClassBuilder(
        non_generic_arguments=MonkDrunkenMasterCustomStarterClassArgs(
            skills=MonkSkillsStatBlock(
                proficiencies={
                    Skill.ACROBATICS: True,
                    Skill.ATHLETICS: False,
                    Skill.HISTORY: False,
                    Skill.INSIGHT: False,
                    Skill.RELIGION: False,
                    Skill.STEALTH: True,
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
            intelligence=8,
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
                Skill.PERFORMANCE,
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
                3: MonkDrunkenMasterLevel3(),
                6: MonkDrunkenMasterLevel6(),
                11: MonkDrunkenMasterLevel11(),
                17: MonkDrunkenMasterLevel17(),
            },
        ),
        tool_proficiencies=[BrewersSupplies()],
    )


class Y2014MonkDrunkenMasterChenWobblejarCharacterBuilder(CharacterBuilder):
    def __init__(self):
        super().__init__(
            name="Chen Wobblejar",
            starter_class_builder=get_starter_class_builder(),
            species_builder=Human.HumanSpeciesBuilder(
                origin_feat=OriginFeats.Alert(),
                skill_proficiency=Skill.PERCEPTION,
            ),
        )
